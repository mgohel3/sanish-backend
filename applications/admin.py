from django.contrib import admin

from .models import ApplicationCategory, ApplicationProject


@admin.register(ApplicationCategory)
class ApplicationCategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "slug", "position", "enabled")
    search_fields = ("label", "slug")


@admin.register(ApplicationProject)
class ApplicationProjectAdmin(admin.ModelAdmin):
    list_display = ("label", "category", "location", "year", "enabled")
    list_filter = ("category",)
    search_fields = ("label", "slug", "location")
