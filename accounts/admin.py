from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivityLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_active", "date_joined")
    list_filter  = ("role", "is_active", "is_staff")
    fieldsets    = BaseUserAdmin.fieldsets + (
        ("CMS Role", {"fields": ("role", "avatar")}),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display  = ("user", "action", "object_repr", "timestamp", "ip")
    list_filter   = ("user",)
    readonly_fields = ("user", "action", "object_repr", "timestamp", "ip")
