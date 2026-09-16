import csv
import io
import json
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponse

from accounts.permissions import SEOManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from seo.models import GlobalSEO, Redirect, SiteSettings, ThemeSettings
from seo.schema_generators import generate_schema_json


class GlobalSEOView(SEOManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        settings = GlobalSEO.get()
        return render(request, "dashboard/seo/global.html", {
            "settings":  settings,
            "active_nav": "seo",
        })

    def post(self, request):
        s = GlobalSEO.get()
        d = request.POST
        s.site_meta_title       = d.get("site_meta_title", "")
        s.site_meta_description = d.get("site_meta_description", "")
        s.site_keywords         = d.get("site_keywords", "")
        s.robots_txt            = d.get("robots_txt", "")
        s.ga4_code              = d.get("ga4_code", "")
        s.gtm_code              = d.get("gtm_code", "")
        s.fb_pixel_code         = d.get("fb_pixel_code", "")
        s.clarity_code          = d.get("clarity_code", "")
        s.gsc_verification_code = d.get("gsc_verification_code", "")
        s.recaptcha_version      = d.get("recaptcha_version", GlobalSEO.RECAPTCHA_OFF)
        s.recaptcha_site_key     = d.get("recaptcha_site_key", "")
        s.recaptcha_secret_key   = d.get("recaptcha_secret_key", "")
        raw_score = d.get("recaptcha_v3_min_score", "").strip()
        try:
            s.recaptcha_v3_min_score = float(raw_score) if raw_score else 0.5
        except ValueError:
            s.recaptcha_v3_min_score = 0.5
        s.save()
        self.log_action("Updated Global SEO settings")
        messages.success(request, "SEO settings saved.")
        return redirect("seo_global")


class RedirectListView(SEOManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/seo/redirects.html", {
            "redirects":  Redirect.objects.all(),
            "active_nav": "seo",
        })

    def post(self, request):
        action = request.POST.get("action", "add")

        if action == "add":
            Redirect.objects.update_or_create(
                source_path=request.POST["source_path"],
                defaults={
                    "destination_path": request.POST["destination_path"],
                    "type":   request.POST.get("type", "301"),
                    "active": True,
                },
            )
            self.log_action("Added redirect", request.POST["source_path"])
            messages.success(request, "Redirect added.")

        elif action == "bulk_csv":
            f = request.FILES.get("csv_file")
            if f:
                reader = csv.DictReader(io.StringIO(f.read().decode("utf-8-sig")))
                count = 0
                for row in reader:
                    src = row.get("source_path", "").strip()
                    dst = row.get("destination_path", "").strip()
                    if src and dst:
                        Redirect.objects.update_or_create(
                            source_path=src,
                            defaults={"destination_path": dst, "type": row.get("type", "301"), "active": True},
                        )
                        count += 1
                self.log_action(f"Bulk imported {count} redirects")
                messages.success(request, f"{count} redirects imported.")

        elif action == "delete":
            rid = request.POST.get("redirect_id")
            Redirect.objects.filter(pk=rid).delete()
            messages.success(request, "Redirect deleted.")

        return redirect("seo_redirects")


class SchemaGeneratorView(SEOManagerRequiredMixin, View):
    SCHEMA_TYPES = ["LocalBusiness", "Product", "FAQPage", "Organization", "Article", "BreadcrumbList"]

    def get(self, request):
        return render(request, "dashboard/seo/schema.html", {
            "schema_types": self.SCHEMA_TYPES,
            "active_nav":   "seo",
        })

    def post(self, request):
        schema_type = request.POST.get("schema_type", "LocalBusiness")
        kwargs = {
            "city":      request.POST.get("city", ""),
            "state":     request.POST.get("state", ""),
            "product":   request.POST.get("product", ""),
            "title":     request.POST.get("title", ""),
            "page_url":  request.POST.get("page_url", ""),
            "faqs":      json.loads(request.POST.get("faqs_json", "[]")),
        }
        schema_json = generate_schema_json(schema_type, **kwargs)
        return render(request, "dashboard/seo/schema.html", {
            "schema_types": self.SCHEMA_TYPES,
            "schema_type":  schema_type,
            "schema_json":  schema_json,
            "active_nav":   "seo",
            **kwargs,
        })


class SiteSettingsView(SEOManagerRequiredMixin, LoggedActionMixin, View):
    _FIELDS = [
        "site_name", "tagline", "logo_dark_url", "logo_light_url", "favicon_url",
        "phone_primary", "phone_secondary", "email_primary", "email_secondary",
        "address_line1", "address_line2", "city", "state", "pincode", "working_hours",
        "map_embed_url", "map_lat", "map_lng",
        "instagram_url", "facebook_url", "youtube_url", "pinterest_url",
        "linkedin_url", "twitter_url", "whatsapp_number",
        "topbar_badge", "header_cta_label", "header_cta_url",
        "footer_description", "footer_copyright", "footer_newsletter_text",
        "smtp_host", "smtp_port", "smtp_username", "smtp_password",
        "smtp_from_email", "smtp_notify_emails",
    ]
    _CHECKBOX_FIELDS = ["smtp_use_tls"]

    _TABS = [
        ("brand",   "Brand & Header"),
        ("contact", "Contact"),
        ("social",  "Social Media"),
        ("map",     "Map"),
        ("footer",  "Footer"),
        ("email",   "Email / SMTP"),
    ]

    def get(self, request):
        settings = SiteSettings.get()
        return render(request, "dashboard/seo/site_settings.html", {
            "s":          settings,
            "tabs":       self._TABS,
            "active_nav": "site_settings",
        })

    def post(self, request):
        s = SiteSettings.get()
        d = request.POST
        tabs = self._TABS  # keep in scope for re-render on error
        for field in self._FIELDS:
            val = d.get(field, "")
            setattr(s, field, val if val is not None else "")
        for field in self._CHECKBOX_FIELDS:
            setattr(s, field, field in d)
        # nullable decimals
        for dec_field in ("map_lat", "map_lng"):
            raw = d.get(dec_field, "").strip()
            setattr(s, dec_field, raw if raw else None)
        # smtp_port must be an int
        raw_port = d.get("smtp_port", "").strip()
        s.smtp_port = int(raw_port) if raw_port.isdigit() else 587
        s.save()
        self.log_action("Updated Site Settings")

        if d.get("action") == "test_email":
            test_to = d.get("test_email_to", "").strip()
            if not test_to:
                messages.error(request, "Enter an email address to send the test to.")
            else:
                try:
                    send_mail(
                        subject="Sanish Laminates — Test Email",
                        message="This is a test email from the Sanish CMS Email/SMTP settings panel. If you received this, your SMTP configuration works.",
                        from_email=s.smtp_from_email or None,
                        recipient_list=[test_to],
                        fail_silently=False,
                        connection=s.get_email_connection(),
                    )
                    messages.success(request, f"Test email sent to {test_to}.")
                except Exception as e:
                    messages.error(request, f"Failed to send test email: {e}")
            return redirect("site_settings")

        messages.success(request, "Site settings saved.")
        return redirect("site_settings")


class ThemeSettingsView(SEOManagerRequiredMixin, LoggedActionMixin, View):
    _FIELDS = [
        "primary_color", "secondary_color", "accent_color", "heading_color", "text_color",
        "link_color", "link_hover_color", "background_color", "header_bg_color",
        "footer_bg_color", "footer_text_color",
        "heading_font", "body_font", "base_font_size",
        "button_style", "button_radius", "button_hover_effect", "button_text_color",
        "container_max_width", "border_radius", "card_shadow_style",
    ]

    _TABS = [
        ("colors",     "Colors"),
        ("typography", "Typography"),
        ("buttons",    "Buttons"),
        ("layout",     "Layout"),
    ]

    def get(self, request):
        settings = ThemeSettings.get()
        return render(request, "dashboard/seo/theme_settings.html", {
            "s":          settings,
            "tabs":       self._TABS,
            "active_nav": "theme_settings",
        })

    def post(self, request):
        s = ThemeSettings.get()
        d = request.POST
        for field in self._FIELDS:
            val = d.get(field, "")
            setattr(s, field, val if val is not None else "")
        s.save()
        self.log_action("Updated Theme Settings")
        messages.success(request, "Theme settings saved.")
        return redirect("theme_settings")
