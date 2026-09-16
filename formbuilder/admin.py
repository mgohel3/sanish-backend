from django.contrib import admin

from .models import FormDefinition, FormField, FormSubmission


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1


@admin.register(FormDefinition)
class FormDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_system", "updated")
    search_fields = ("name", "slug")
    inlines = [FormFieldInline]


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ("form", "created", "source_page")
    list_filter = ("form",)
    readonly_fields = ("form", "data", "source_page", "created")
