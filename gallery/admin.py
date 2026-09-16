from django.contrib import admin

from .models import GalleryCatalogue, GalleryImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


@admin.register(GalleryCatalogue)
class GalleryCatalogueAdmin(admin.ModelAdmin):
    list_display = ("label", "slug", "position", "enabled")
    search_fields = ("label", "slug")
    inlines = [GalleryImageInline]
