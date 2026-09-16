"""
Design Gallery management — the catalogues (S'Shades, Thre3, Cool Colour,
Perspective V4, Thermo) and their photos that power the real /applications
and /applications/gallery/<catalogue> pages. Seeded from the 346 images that
already existed on disk (see gallery/migrations/0002_seed_gallery.py); this
gives the CMS add/remove/reorder control over the same content going forward
without needing server file-system access.
"""
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from media_library.models import MediaAsset
from gallery.models import GalleryCatalogue, GalleryImage


class GalleryCatalogueListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        return render(request, "dashboard/gallery/catalogue_list.html", {
            "catalogues": GalleryCatalogue.objects.all(),
            "active_nav": "gallery",
        })


class GalleryCatalogueCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/gallery/catalogue_form.html", {"active_nav": "gallery"})

    def post(self, request):
        d = request.POST
        last = GalleryCatalogue.objects.order_by("-position").first()
        cat = GalleryCatalogue.objects.create(
            slug=d["slug"].strip(),
            label=d["label"].strip(),
            cover_image=d.get("cover_image", "").strip(),
            position=(last.position + 1) if last else 0,
            enabled=("enabled" in d),
        )
        self.log_action("Created gallery catalogue", cat)
        messages.success(request, f"Catalogue “{cat.label}” created.")
        return redirect("gallery_catalogue_list")


class GalleryCatalogueEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        cat = get_object_or_404(GalleryCatalogue, pk=pk)
        return render(request, "dashboard/gallery/catalogue_form.html", {
            "catalogue": cat, "active_nav": "gallery",
        })

    def post(self, request, pk):
        cat = get_object_or_404(GalleryCatalogue, pk=pk)
        d = request.POST
        cat.label = d["label"].strip()
        cat.cover_image = d.get("cover_image", "").strip()
        cat.enabled = "enabled" in d
        cat.save()
        self.log_action("Updated gallery catalogue", cat)
        messages.success(request, f"“{cat.label}” saved.")
        return redirect("gallery_catalogue_list")


class GalleryCatalogueDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        cat = get_object_or_404(GalleryCatalogue, pk=pk)
        label = cat.label
        self.log_action("Deleted gallery catalogue", cat)
        cat.delete()
        messages.success(request, f"Catalogue “{label}” deleted.")
        return redirect("gallery_catalogue_list")


# ── Photos within a catalogue ─────────────────────────────────────────────────

class GalleryImageListView(ContentManagerRequiredMixin, View):
    """The main "manage photos" screen — grid view, multi-upload, inline
    product-code editing, drag reorder, delete. Built for catalogues with
    up to 100+ photos, so images are individual rows (not one big JSON blob)."""

    def get(self, request, pk):
        catalogue = get_object_or_404(GalleryCatalogue, pk=pk)
        return render(request, "dashboard/gallery/image_list.html", {
            "catalogue": catalogue,
            "images": catalogue.images.all(),
            "active_nav": "gallery",
        })

    def post(self, request, pk):
        """Bulk-save product codes edited inline in the grid."""
        catalogue = get_object_or_404(GalleryCatalogue, pk=pk)
        for image in catalogue.images.all():
            key = f"product_id_{image.pk}"
            if key in request.POST:
                image.product_id = request.POST[key].strip()
                image.save(update_fields=["product_id"])
        self.log_action(f"Updated photo codes for “{catalogue.label}”", catalogue)
        messages.success(request, "Product codes saved.")
        return redirect("gallery_image_list", pk=pk)


class GalleryImageUploadView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    """AJAX endpoint — one call per file (the page loops over a multi-file
    picker). Uploads straight into the Media Library and creates the
    GalleryImage row in the same request."""

    def post(self, request, pk):
        catalogue = get_object_or_404(GalleryCatalogue, pk=pk)
        f = request.FILES.get("file")
        if not f:
            return JsonResponse({"error": "No file"}, status=400)

        asset = MediaAsset(
            file=f, title=f.name.rsplit(".", 1)[0][:300],
            original_filename=f.name, uploaded_by=request.user,
        )
        asset.save()

        last = catalogue.images.order_by("-position").first()
        image = GalleryImage.objects.create(
            catalogue=catalogue,
            image=asset.url,
            product_id=f.name.rsplit(".", 1)[0][:40],
            position=(last.position + 1) if last else 0,
        )
        self.log_action(f"Uploaded photo to “{catalogue.label}”", image)
        return JsonResponse({"id": image.pk, "src": image.image, "product_id": image.product_id})


class GalleryImageReorderView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        catalogue = get_object_or_404(GalleryCatalogue, pk=pk)
        try:
            order = json.loads(request.body).get("order", [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"ok": False, "error": "bad payload"}, status=400)
        for pos, image_id in enumerate(order):
            GalleryImage.objects.filter(pk=image_id, catalogue=catalogue).update(position=pos)
        self.log_action(f"Reordered “{catalogue.label}” photos", catalogue)
        return JsonResponse({"ok": True})


class GalleryImageDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk, image_id):
        image = get_object_or_404(GalleryImage, pk=image_id, catalogue_id=pk)
        self.log_action("Deleted gallery photo", image)
        image.delete()
        return JsonResponse({"ok": True})
