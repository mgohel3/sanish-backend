from django.contrib import admin

from .models import Faq


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ["question", "source_post", "position", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["question", "answer"]
