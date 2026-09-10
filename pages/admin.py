from django.contrib import admin
from .models import PageTemplate, CityPage, SitePage, PageSection


class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 0
    fields = ("position", "block_type", "label", "anchor_id", "enabled")
    ordering = ("position",)


@admin.register(SitePage)
class SitePageAdmin(admin.ModelAdmin):
    list_display  = ("title", "slug", "path", "position", "is_system")
    list_editable = ("position",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PageSectionInline]


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ("page", "position", "label", "block_type", "enabled")
    list_filter  = ("page", "block_type", "enabled")
    ordering     = ("page", "position")


@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "product_type_label", "created")


@admin.register(CityPage)
class CityPageAdmin(admin.ModelAdmin):
    list_display  = ("city", "state", "template", "slug", "status", "created")
    list_filter   = ("status", "template", "state")
    search_fields = ("city", "slug")
    prepopulated_fields = {"slug": ()}
