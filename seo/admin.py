from django.contrib import admin
from .models import GlobalSEO, Redirect


@admin.register(GlobalSEO)
class GlobalSEOAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not GlobalSEO.objects.exists()


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display  = ("source_path", "destination_path", "type", "active")
    list_filter   = ("type", "active")
    search_fields = ("source_path", "destination_path")
