"""
Form builder — CMS-managed forms with fields the client can add, remove and
reorder without a developer. Deliberately separate from ``leads.Inquiry`` /
the existing hard-coded ``ContactForm`` pipeline, which stays untouched.
"""
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.permissions import AdminRequiredMixin, SalesManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from formbuilder.models import FIELD_TYPES, FormDefinition, FormField


def _parse_options(raw: str) -> list:
    return [line.strip() for line in (raw or "").splitlines() if line.strip()]


# Forms still fully built into the site's code, with no CMS FormDefinition
# behind them yet — listed for visibility only. Contact Form, the Inquiry
# Popup and the Sample Request form used to be listed here too; they're now
# real (system) FormDefinition rows above, field-editable from this screen,
# still feeding ``leads.Inquiry`` exactly as before. The Collection Inquiry
# Form remains code-only: it maps its "purpose" selection to different
# Inquiry types (contact/dealer/architect) client-side, a business-specific
# behavior better left as code for now than force-fit into one field set.
LEGACY_FORMS = [
    {
        "name": "Collection Inquiry Form",
        "location": "/collection",
        "inquiry_type": "",
        "fields": "Name, Email, Phone, Collection, Purpose, Message",
    },
]


class FormListView(AdminRequiredMixin, View):
    """The "Forms" index — CMS-managed forms plus a read-only inventory of the
    forms still built into the site's code."""

    def get(self, request):
        forms = FormDefinition.objects.all()
        return render(request, "dashboard/forms/list.html", {
            "forms": forms,
            "legacy_forms": LEGACY_FORMS,
            "active_nav": "forms",
        })


class FormCreateView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/forms/settings.html", {
            "form_obj": None,
            "active_nav": "forms",
            "default_auto_reply_subject": FormDefinition._meta.get_field("auto_reply_subject").get_default(),
            "default_auto_reply_body": FormDefinition._meta.get_field("auto_reply_body").get_default(),
        })

    def post(self, request):
        d = request.POST
        form = FormDefinition.objects.create(
            slug=d["slug"].strip(),
            name=d["name"].strip(),
            description=d.get("description", "").strip(),
            submit_label=d.get("submit_label") or "Submit",
            success_message=d.get("success_message") or "Thank you! We'll be in touch shortly.",
            notify_emails=d.get("notify_emails", "").strip(),
            target_pipeline=d.get("target_pipeline") or FormDefinition.TARGET_SUBMISSION,
            inquiry_type=d.get("inquiry_type", "").strip(),
            auto_reply_enabled=("auto_reply_enabled" in d),
            auto_reply_subject=d.get("auto_reply_subject", "").strip()
                or FormDefinition._meta.get_field("auto_reply_subject").get_default(),
            auto_reply_body=d.get("auto_reply_body", "").strip()
                or FormDefinition._meta.get_field("auto_reply_body").get_default(),
            webhook_enabled=("webhook_enabled" in d),
            webhook_url=d.get("webhook_url", "").strip(),
            webhook_secret=d.get("webhook_secret", "").strip(),
        )
        self.log_action("Created form", form)
        messages.success(request, f"Form “{form.name}” created. Now add its fields.")
        return redirect("form_field_list", slug=form.slug)


class FormSettingsEditView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, slug):
        form = get_object_or_404(FormDefinition, slug=slug)
        return render(request, "dashboard/forms/settings.html", {
            "form_obj": form,
            "active_nav": "forms",
            "default_auto_reply_subject": FormDefinition._meta.get_field("auto_reply_subject").get_default(),
            "default_auto_reply_body": FormDefinition._meta.get_field("auto_reply_body").get_default(),
        })

    def post(self, request, slug):
        form = get_object_or_404(FormDefinition, slug=slug)
        d = request.POST
        form.name = d["name"].strip()
        form.description = d.get("description", "").strip()
        form.submit_label = d.get("submit_label") or "Submit"
        form.success_message = d.get("success_message") or form.success_message
        form.notify_emails = d.get("notify_emails", "").strip()
        form.target_pipeline = d.get("target_pipeline") or FormDefinition.TARGET_SUBMISSION
        form.inquiry_type = d.get("inquiry_type", "").strip()
        form.auto_reply_enabled = "auto_reply_enabled" in d
        form.auto_reply_subject = d.get("auto_reply_subject", "").strip()
        form.auto_reply_body = d.get("auto_reply_body", "").strip()
        form.webhook_enabled = "webhook_enabled" in d
        form.webhook_url = d.get("webhook_url", "").strip()
        form.webhook_secret = d.get("webhook_secret", "").strip()
        form.save()
        self.log_action("Updated form settings", form)
        messages.success(request, f"“{form.name}” settings saved.")
        return redirect("form_field_list", slug=form.slug)


class FormDeleteView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug):
        form = get_object_or_404(FormDefinition, slug=slug)
        if form.is_system:
            messages.error(request, "System forms cannot be deleted.")
            return redirect("form_list")
        name = form.name
        self.log_action("Deleted form", form)
        form.delete()
        messages.success(request, f"Form “{name}” deleted.")
        return redirect("form_list")


class FormFieldListView(AdminRequiredMixin, View):
    def get(self, request, slug):
        form = get_object_or_404(FormDefinition, slug=slug)
        return render(request, "dashboard/forms/fields.html", {
            "form_obj": form,
            "form_fields": form.fields.all(),
            "active_nav": "forms",
        })


class FormFieldReorderView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug):
        form = get_object_or_404(FormDefinition, slug=slug)
        try:
            order = json.loads(request.body).get("order", [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"ok": False, "error": "bad payload"}, status=400)
        for pos, pk in enumerate(order):
            FormField.objects.filter(pk=pk, form=form).update(position=pos)
        self.log_action(f"Reordered “{form.name}” fields", form)
        return JsonResponse({"ok": True})


class FormFieldCreateView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, slug):
        form = get_object_or_404(FormDefinition, slug=slug)
        return render(request, "dashboard/forms/field_form.html", {
            "form_obj": form,
            "field": None,
            "FIELD_TYPES": FIELD_TYPES,
            "active_nav": "forms",
        })

    def post(self, request, slug):
        form = get_object_or_404(FormDefinition, slug=slug)
        d = request.POST
        last = form.fields.order_by("-position").first()
        field = FormField.objects.create(
            form=form,
            field_type=d.get("field_type", "text"),
            name=d["name"].strip(),
            label=d["label"].strip(),
            placeholder=d.get("placeholder", "").strip(),
            help_text=d.get("help_text", "").strip(),
            required=("required" in d),
            options=_parse_options(d.get("options", "")),
            position=(last.position + 1) if last else 0,
        )
        self.log_action("Added form field", field)
        messages.success(request, f"Field “{field.label}” added.")
        return redirect("form_field_list", slug=slug)


class FormFieldEditView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, slug, pk):
        field = get_object_or_404(FormField, pk=pk, form__slug=slug)
        return render(request, "dashboard/forms/field_form.html", {
            "form_obj": field.form,
            "field": field,
            "FIELD_TYPES": FIELD_TYPES,
            "active_nav": "forms",
        })

    def post(self, request, slug, pk):
        field = get_object_or_404(FormField, pk=pk, form__slug=slug)
        d = request.POST
        field.field_type = d.get("field_type", "text")
        field.name = d["name"].strip()
        field.label = d["label"].strip()
        field.placeholder = d.get("placeholder", "").strip()
        field.help_text = d.get("help_text", "").strip()
        field.required = "required" in d
        field.options = _parse_options(d.get("options", ""))
        field.save()
        self.log_action("Updated form field", field)
        messages.success(request, f"Field “{field.label}” saved.")
        return redirect("form_field_list", slug=slug)


class FormFieldDeleteView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug, pk):
        field = get_object_or_404(FormField, pk=pk, form__slug=slug)
        label = field.label
        self.log_action("Deleted form field", field)
        field.delete()
        messages.success(request, f"Field “{label}” deleted.")
        return redirect("form_field_list", slug=slug)


class FormSubmissionListView(SalesManagerRequiredMixin, View):
    def get(self, request, slug):
        form = get_object_or_404(FormDefinition, slug=slug)
        submissions = form.submissions.all()
        return render(request, "dashboard/forms/submissions.html", {
            "form_obj": form,
            "submissions": submissions,
            "active_nav": "forms",
        })
