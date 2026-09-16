from urllib.parse import urlencode

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count

from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from media_library.models import MediaAsset, MediaFolder
from media_library.utils import scan_media_root, import_external_dir, get_import_dirs


class MediaLibraryView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    template_name = "dashboard/media/library.html"

    # ── helpers ───────────────────────────────────────────────────────────────
    def _redirect_back(self, request):
        params = {}
        for key in ("type", "folder", "q"):
            val = request.POST.get(key) or request.GET.get(key)
            if val:
                params[key] = val
        url = "/cms/media/"
        if params:
            url = f"{url}?{urlencode(params)}"
        return redirect(url)

    def _ids(self, request):
        raw = []
        for v in request.POST.getlist("ids"):
            raw.extend(v.split(","))
        return [i for i in (s.strip() for s in raw) if i.isdigit()]

    # ── GET ───────────────────────────────────────────────────────────────────
    def get(self, request):
        qs = MediaAsset.objects.select_related("folder", "uploaded_by").order_by("-created")

        type_f = request.GET.get("type", "")
        folder = request.GET.get("folder", "")
        q      = request.GET.get("q", "")

        if type_f:
            qs = qs.filter(type=type_f)
        if folder == "none":
            qs = qs.filter(folder__isnull=True)
        elif folder:
            qs = qs.filter(folder_id=folder)
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(alt_text__icontains=q) | qs.filter(original_filename__icontains=q)

        folders = MediaFolder.objects.annotate(n=Count("assets")).order_by("name")

        return render(request, self.template_name, {
            "assets":  qs,
            "folders": folders,
            "total_count": MediaAsset.objects.count(),
            "uncategorized_count": MediaAsset.objects.filter(folder__isnull=True).count(),
            "type_f": type_f, "folder": folder, "q": q,
            "type_choices": MediaAsset.TYPE_CHOICES,
            "active": "media", "active_nav": "media",
        })

    # ── POST ──────────────────────────────────────────────────────────────────
    def post(self, request):
        action = request.POST.get("action", "upload")

        if action == "upload":
            files = request.FILES.getlist("files")
            folder_id = request.POST.get("upload_folder") or None
            created = 0
            for f in files:
                asset = MediaAsset(
                    file=f,
                    title=f.name.rsplit(".", 1)[0][:300],
                    original_filename=f.name,
                    folder_id=folder_id,
                    uploaded_by=request.user,
                )
                asset.save()
                created += 1
            if created:
                messages.success(request, f"{created} file(s) uploaded.")
                self.log_action("Uploaded media")
            else:
                messages.warning(request, "No files were selected.")

        elif action == "update":
            asset = get_object_or_404(MediaAsset, pk=request.POST.get("pk"))
            asset.title       = request.POST.get("title", "").strip()
            asset.alt_text    = request.POST.get("alt_text", "").strip()
            asset.caption     = request.POST.get("caption", "").strip()
            asset.description  = request.POST.get("description", "").strip()
            folder_id = request.POST.get("folder") or None
            asset.folder_id = folder_id
            asset.save()
            messages.success(request, "Media details saved.")
            self.log_action("Updated media", asset)

        elif action == "delete":
            MediaAsset.objects.filter(pk=request.POST.get("pk")).delete()
            messages.success(request, "Media deleted.")
            self.log_action("Deleted media")

        elif action == "bulk_delete":
            ids = self._ids(request)
            n, _ = MediaAsset.objects.filter(pk__in=ids).delete()
            messages.success(request, f"{len(ids)} item(s) deleted.")
            self.log_action("Bulk-deleted media")

        elif action == "bulk_move":
            ids = self._ids(request)
            folder_id = request.POST.get("folder") or None
            MediaAsset.objects.filter(pk__in=ids).update(folder_id=folder_id)
            messages.success(request, f"{len(ids)} item(s) moved.")
            self.log_action("Moved media")

        elif action == "folder_create":
            name = request.POST.get("name", "").strip()
            if name:
                MediaFolder.objects.get_or_create(name=name)
                messages.success(request, f"Folder “{name}” created.")
            else:
                messages.warning(request, "Folder name is required.")

        elif action == "folder_rename":
            folder = get_object_or_404(MediaFolder, pk=request.POST.get("pk"))
            name = request.POST.get("name", "").strip()
            if name:
                folder.name = name
                folder.save()
                messages.success(request, "Folder renamed.")

        elif action == "folder_delete":
            folder = get_object_or_404(MediaFolder, pk=request.POST.get("pk"))
            # Assets are kept — folder FK is SET_NULL, so they fall back to Uncategorized.
            folder.delete()
            messages.success(request, "Folder deleted. Its media moved to Uncategorized.")

        elif action == "scan_disk":
            added, skipped = scan_media_root()
            messages.success(request, f"Disk scan complete — {added} new file(s) registered, {skipped} already known.")
            self.log_action("Scanned media disk")

        elif action == "import_frontend":
            total_added = total_skipped = 0
            found_any = False
            for d in get_import_dirs():
                if d.is_dir():
                    found_any = True
                    a, s = import_external_dir(str(d), folder_name="Frontend")
                    total_added += a
                    total_skipped += s
            if found_any:
                messages.success(
                    request,
                    f"Frontend import complete — {total_added} image(s) added, {total_skipped} already imported.",
                )
                self.log_action("Imported frontend media")
            else:
                messages.warning(request, "No frontend image folders found to import from.")

        return self._redirect_back(request)


class MediaUploadAjaxView(ContentManagerRequiredMixin, View):
    """HTMX / JSON upload endpoint for inline use in other forms."""
    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            return JsonResponse({"error": "No file"}, status=400)
        asset = MediaAsset(
            file=f, title=f.name.rsplit(".", 1)[0][:300],
            original_filename=f.name, uploaded_by=request.user,
        )
        asset.save()
        return JsonResponse({
            "id":  asset.pk,
            "url": asset.url,
            "original_url": asset.original_url,
            "alt": asset.alt_text,
            "title": asset.title,
            "type": asset.type,
        })


class MediaPickerListView(ContentManagerRequiredMixin, View):
    """
    JSON feed for the reusable "Choose from Media Library" picker used in the
    Home Page, Blog, Product and City Page forms. Read-only.
    """
    PAGE_SIZE = 60

    def get(self, request):
        qs = MediaAsset.objects.select_related("folder").order_by("-created")

        type_f = request.GET.get("type", "").strip()
        folder = request.GET.get("folder", "").strip()
        q      = request.GET.get("q", "").strip()

        if type_f in {"image", "video", "pdf", "other"}:
            qs = qs.filter(type=type_f)
        if folder == "none":
            qs = qs.filter(folder__isnull=True)
        elif folder.isdigit():
            qs = qs.filter(folder_id=folder)
        if q:
            qs = (qs.filter(title__icontains=q)
                  | qs.filter(alt_text__icontains=q)
                  | qs.filter(original_filename__icontains=q))

        try:
            page = max(1, int(request.GET.get("page", 1)))
        except (TypeError, ValueError):
            page = 1
        start = (page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        window = list(qs[start:end + 1])
        has_more = len(window) > self.PAGE_SIZE
        window = window[:self.PAGE_SIZE]

        results = [{
            "id": a.pk,
            "url": a.url,
            "original_url": a.original_url,
            "title": a.title or a.filename,
            "filename": a.filename,
            "type": a.type,
            "alt_text": a.alt_text,
        } for a in window]

        folders = [{"id": "", "name": "All folders"},
                   {"id": "none", "name": "Uncategorized"}]
        folders += [{"id": f.pk, "name": f.name}
                    for f in MediaFolder.objects.order_by("name")]

        return JsonResponse({
            "results": results,
            "folders": folders,
            "page": page,
            "has_more": has_more,
        })
