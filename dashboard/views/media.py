from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse

from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from media_library.models import MediaAsset, MediaFolder


class MediaLibraryView(ContentManagerRequiredMixin, View):
    def get(self, request):
        qs     = MediaAsset.objects.select_related("folder", "uploaded_by").order_by("-created")
        type_f = request.GET.get("type", "")
        folder = request.GET.get("folder", "")
        q      = request.GET.get("q", "")
        if type_f:
            qs = qs.filter(type=type_f)
        if folder:
            qs = qs.filter(folder_id=folder)
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(alt_text__icontains=q)
        return render(request, "dashboard/media/library.html", {
            "assets":  qs,
            "folders": MediaFolder.objects.all(),
            "type_f": type_f, "folder": folder, "q": q,
            "active_nav": "media",
        })

    def post(self, request):
        action = request.POST.get("action", "upload")
        if action == "upload":
            files  = request.FILES.getlist("files")
            folder_id = request.POST.get("folder") or None
            for f in files:
                asset = MediaAsset(
                    file=f,
                    title=f.name,
                    folder_id=folder_id,
                    uploaded_by=request.user,
                )
                asset.save()
            messages.success(request, f"{len(files)} file(s) uploaded.")
        elif action == "update_alt":
            asset = get_object_or_404(MediaAsset, pk=request.POST.get("pk"))
            asset.alt_text = request.POST.get("alt_text", "")
            asset.title    = request.POST.get("title", "")
            asset.save()
            messages.success(request, "Updated.")
        elif action == "delete":
            MediaAsset.objects.filter(pk=request.POST.get("pk")).delete()
            messages.success(request, "Deleted.")
        return redirect("media_library")


class MediaUploadAjaxView(ContentManagerRequiredMixin, View):
    """HTMX / JSON upload endpoint for inline use in other forms."""
    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            return JsonResponse({"error": "No file"}, status=400)
        asset = MediaAsset(file=f, title=f.name, uploaded_by=request.user)
        asset.save()
        return JsonResponse({
            "id":  asset.pk,
            "url": asset.url,
            "alt": asset.alt_text,
            "title": asset.title,
        })
