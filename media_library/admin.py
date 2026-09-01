from django.contrib import admin
from .models import MediaAsset, MediaFolder


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display  = ("title", "type", "folder", "uploaded_by", "created")
    list_filter   = ("type", "folder")
    search_fields = ("title", "alt_text")
    readonly_fields = ("webp_version", "width", "height", "created")
