"""Applications photo TAGS (spaces) + bulk CSV tagging.

* ``/cms/gallery/spaces/``     — the space tags themselves (Kitchen, Bedroom, …): add / rename / reorder / hide / delete.
* ``/cms/gallery/tag-import/`` — upload a CSV (image filename, SKU, catalogue, tags), review a preview, then commit.

The CSV never creates photos or tags: the filename is the key for an EXISTING photo (re-uploading the same CSV just updates
the same photos again), and any tag that doesn't exist yet is flagged in the preview and skipped.
"""
import csv
import io
import json

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from gallery.models import GalleryCatalogue, GalleryImage, GallerySpace
from gallery.utils import build_preview, commit_rows, decode_upload, parse_tag_csv, tag_key


class GallerySpaceListView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        spaces = list(GallerySpace.objects.all())
        for s in spaces:
            s.photo_count = s.images.count()
        return render(request, "dashboard/gallery/spaces.html", {"spaces": spaces, "active_nav": "gallery"})

    def post(self, request):
        action = request.POST.get("action", "")
        if action == "create":
            label = request.POST.get("label", "").strip()[:80]
            if not label:
                messages.error(request, "Give the space a name.")
            elif any(tag_key(s.label) == tag_key(label) for s in GallerySpace.objects.all()):
                messages.error(request, f"A space like “{label}” already exists.")
            else:
                from django.utils.text import slugify
                base = slugify(label) or "space"
                slug, n = base, 2
                while GallerySpace.objects.filter(slug=slug).exists():
                    slug, n = f"{base}-{n}", n + 1
                last = GallerySpace.objects.order_by("-position").first()
                s = GallerySpace.objects.create(slug=slug, label=label, position=(last.position + 1) if last else 0)
                self.log_action("Created gallery space", s)
                messages.success(request, f"Space “{label}” added.")
        elif action == "save":
            for s in GallerySpace.objects.all():
                label = request.POST.get(f"label_{s.pk}", "").strip()[:80]
                if label and label != s.label and not GallerySpace.objects.filter(label=label).exclude(pk=s.pk).exists():
                    s.label = label
                s.enabled = f"enabled_{s.pk}" in request.POST
                pos = request.POST.get(f"position_{s.pk}", "")
                if pos.isdigit():
                    s.position = int(pos)
                s.save()
            self.log_action("Updated gallery spaces")
            messages.success(request, "Spaces saved.")
        return redirect("gallery_space_list")


class GallerySpaceDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        s = get_object_or_404(GallerySpace, pk=pk)
        n = s.images.count()
        if n:
            messages.error(request, f"“{s.label}” is used by {n} photo(s). Untick “Show” to hide it instead, or remove it from those photos first.")
        else:
            self.log_action("Deleted gallery space", s)
            s.delete()
            messages.success(request, "Space deleted.")
        return redirect("gallery_space_list")


class GalleryTagImportView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    template_name = "dashboard/gallery/tag_import.html"

    def _ctx(self, **extra):
        return {
            "spaces": GallerySpace.objects.filter(enabled=True),
            "photo_count": GalleryImage.objects.count(),
            "active_nav": "gallery",
            **extra,
        }

    def get(self, request):
        return render(request, self.template_name, self._ctx())

    def post(self, request):
        action = request.POST.get("action", "preview")

        if action == "download_template":
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["image filename", "SKU", "catalogue", "tags"])
            w.writerow(["thre3_3003_01.jpg", "3003", "Thre3", "Bedroom|Wardrobes"])
            w.writerow(["thre3_3012_01.jpg", "3012", "Thre3", "Kitchen"])
            resp = HttpResponse(buf.getvalue(), content_type="text/csv")
            resp["Content-Disposition"] = 'attachment; filename="applications-tags-template.csv"'
            return resp

        if action == "commit":
            try:
                results = json.loads(request.POST.get("results", "[]"))
            except json.JSONDecodeError:
                results = []
            updated = commit_rows(results)
            self.log_action(f"Bulk tag import: {updated} photos updated")
            messages.success(request, f"Done — {updated} photo(s) updated. Nothing was created; unknown tags were skipped.")
            return redirect("gallery_tag_import")

        # preview
        f = request.FILES.get("csv_file")
        if not f:
            messages.error(request, "Choose a CSV file first.")
            return redirect("gallery_tag_import")
        rows, error = parse_tag_csv(decode_upload(f.read()))
        if error:
            messages.error(request, error)
            return redirect("gallery_tag_import")
        results, summary = build_preview(rows)
        return render(request, self.template_name, self._ctx(
            results=results,
            summary=summary,
            results_json=json.dumps(results),
            ready_count=summary["matched"],
            filename=f.name,
        ))
