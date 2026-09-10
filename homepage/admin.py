from django.contrib import admin

from .models import HomeSection


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display  = ("label", "block_type", "position", "enabled", "updated")
    list_editable = ("position", "enabled")
    list_filter   = ("enabled", "block_type")
    ordering      = ("position",)
