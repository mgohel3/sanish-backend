from django.contrib import admin
from .models import PageTemplate, CityPage


@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "product_type_label", "created")


@admin.register(CityPage)
class CityPageAdmin(admin.ModelAdmin):
    list_display  = ("city", "state", "template", "slug", "status", "created")
    list_filter   = ("status", "template", "state")
    search_fields = ("city", "slug")
    prepopulated_fields = {"slug": ()}
