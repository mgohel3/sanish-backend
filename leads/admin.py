from django.contrib import admin
from .models import Inquiry, Dealer


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display  = ("name", "type", "email", "phone", "city", "status", "created")
    list_filter   = ("type", "status")
    search_fields = ("name", "email", "phone")


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display  = ("name", "city", "state", "phone", "status")
    list_filter   = ("status", "state")
    search_fields = ("name", "city")
