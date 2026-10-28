import csv
import io
import json
import re
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponse

from accounts.permissions import SEOManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from seo.models import GlobalSEO, PageSEO, Redirect, SiteSettings, ThemeSettings
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


class PageSEOView(SEOManagerRequiredMixin, LoggedActionMixin, View):
    """One card per fixed page: title, description, share image, noindex. Saved together with one button."""

    def get(self, request):
        from pages.models import SitePage
        have = set(PageSEO.objects.values_list("path", flat=True))
        for sp in SitePage.objects.all():
            path = getattr(sp, "path", "") or ""
            if path and path not in have:
                PageSEO.objects.create(path=path, label=sp.title, position=100)
                have.add(path)
        return render(request, "dashboard/seo/pages.html", {"pages": PageSEO.objects.all(), "active_nav": "seo_pages"})

    def post(self, request):
        d = request.POST
        for p in PageSEO.objects.all():
            k = str(p.pk)
            if f"title_{k}" not in d:
                continue
            p.meta_title       = d.get(f"title_{k}", "").strip()
            p.meta_description = d.get(f"desc_{k}", "").strip()
            p.og_image         = d.get(f"og_{k}", "").strip()
            p.noindex          = d.get(f"noindex_{k}") == "on"
            p.save()
        self.log_action("Updated Page SEO")
        messages.success(request, "Page SEO saved. It goes live on the website within a few seconds.")
        return redirect("seo_pages")


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


class SiteModeView(SEOManagerRequiredMixin, LoggedActionMixin, View):
    """Coming soon / maintenance page switch. Only the site_mode_* fields are ever written here."""

    def get(self, request):
        return render(request, "dashboard/seo/site_mode.html", {"s": SiteSettings.get(), "active_nav": "site_mode"})

    def post(self, request):
        s = SiteSettings.get()
        d = request.POST
        mode = d.get("site_mode", "off")
        s.site_mode = mode if mode in ("off", "coming_soon", "maintenance") else "off"
        la = d.get("site_mode_launch_at", "").strip()
        s.site_mode_launch_at = la if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", la) else ""
        s.site_mode_title = d.get("site_mode_title", "").strip()[:200]
        s.site_mode_message = d.get("site_mode_message", "").strip()[:600]
        s.site_mode_show_timer = "site_mode_show_timer" in d
        s.site_mode_auto_open = "site_mode_auto_open" in d
        key = re.sub(r"[^A-Za-z0-9_-]", "", d.get("site_mode_bypass_key", "").strip())[:40]
        s.site_mode_bypass_key = key or "sanish-preview"
        s.save()
        self.log_action("Updated site mode", s)
        messages.success(request, "Site mode saved - it is live on the website now.")
        return redirect("site_mode")


class SiteSettingsView(SEOManagerRequiredMixin, LoggedActionMixin, View):
    _FIELDS = [
        "site_name", "tagline", "designs_count", "logo_dark_url", "logo_light_url", "favicon_url",
        "phone_primary", "phone_secondary", "email_primary", "email_secondary",
        "address_line1", "address_line2", "city", "state", "pincode", "working_hours",
        "map_embed_url", "map_lat", "map_lng",
        "instagram_url", "facebook_url", "youtube_url", "pinterest_url",
        "linkedin_url", "twitter_url", "whatsapp_number",
        "topbar_badge", "header_cta_label", "header_cta_url",
        "footer_description", "footer_copyright", "footer_newsletter_text",
        "footer_social_title", "footer_social_title_font", "footer_social_title_color", "footer_order",
        "sound_url", "sound_position",
        "mobile_menu_style", "mobile_menu_theme", "mobile_menu_bg_color", "mobile_menu_bg_image", "mobile_menu_logo_url",
        "mobile_menu_effect", "mobile_menu_overlay", "mobile_menu_layout", "mobile_menu_motion",
        "smtp_host", "smtp_port", "smtp_username", "smtp_password",
        "smtp_from_email", "smtp_notify_emails",
    ]
    _CHECKBOX_FIELDS = ["smtp_use_tls", "footer_show_newsletter", "footer_show_apps", "footer_show_social", "footer_social_show_title", "sound_enabled", "sound_show_button", "mobile_menu_show_catalogue", "mobile_menu_show_contact", "mobile_menu_show_social"]

    _TABS = [
        ("brand",   "Brand & Header"),
        ("contact", "Contact"),
        ("social",  "Social Media"),
        ("map",     "Map"),
        ("footer",  "Footer"),
        ("mobile",  "Mobile Menu"),
        ("sound",   "Sound"),
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
            if field in d:  # a field that was not submitted keeps its value (a partial POST must never blank settings)
                setattr(s, field, d.get(field) or "")
        for field in self._CHECKBOX_FIELDS:
            setattr(s, field, field in d)
        # nullable decimals
        for dec_field in ("map_lat", "map_lng"):
            raw = d.get(dec_field, "").strip()
            setattr(s, dec_field, raw if raw else None)
        # smtp_port must be an int
        raw_port = d.get("smtp_port", "").strip()
        s.smtp_port = int(raw_port) if raw_port.isdigit() else 587
        raw_size = d.get("footer_social_icon_size", "").strip()
        s.footer_social_icon_size = min(72, max(24, int(raw_size))) if raw_size.isdigit() else 38
        if s.footer_social_title_font not in ("", "serif", "sans"):
            s.footer_social_title_font = ""
        color = s.footer_social_title_color.strip()
        s.footer_social_title_color = color if re.fullmatch(r"#[0-9a-fA-F]{3,8}", color) else ""
        s.footer_order = ",".join(s.footer_order_list)  # keep only known keys, in the dragged order
        # Sound: accept only a site path or http(s) URL, and keep the numbers in range
        url = s.sound_url.strip()
        s.sound_url = url if re.match(r"^(/|https?://)", url) else ""
        if s.sound_position not in ("left", "right"):
            s.sound_position = "left"
        # Mobile menu: only known styles/themes, a hex colour, and site-path / http(s) image URLs
        if s.mobile_menu_style not in ("drawer_right", "drawer_left", "fullscreen"):
            s.mobile_menu_style = "drawer_right"
        if s.mobile_menu_theme not in ("light", "dark", "brand"):
            s.mobile_menu_theme = "light"
        if s.mobile_menu_effect not in ("plain", "glass", "liquid", "image"):
            s.mobile_menu_effect = "liquid"
        if s.mobile_menu_layout not in ("list", "tiles"):
            s.mobile_menu_layout = "list"
        if s.mobile_menu_motion not in ("off", "slow", "normal", "fast"):
            s.mobile_menu_motion = "normal"
        ov = s.mobile_menu_overlay.strip()
        s.mobile_menu_overlay = str(min(90, max(0, int(ov)))) if ov.isdigit() else "60"
        mc = s.mobile_menu_bg_color.strip()
        s.mobile_menu_bg_color = mc if re.fullmatch(r"#[0-9a-fA-F]{3,8}", mc) else ""
        for f in ("mobile_menu_bg_image", "mobile_menu_logo_url"):
            u = getattr(s, f).strip()
            setattr(s, f, u if re.match(r"^(/|https?://)", u) else "")
        raw_h = d.get("sound_button_size", "").strip()
        if raw_h.isdigit():
            s.sound_button_size = min(72, max(28, int(raw_h)))
        raw_v = d.get("sound_volume", "").strip()
        if raw_v.isdigit():
            s.sound_volume = min(100, int(raw_v))
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
            if field in d:  # a field that was not submitted keeps its value (a partial POST must never blank settings)
                setattr(s, field, d.get(field) or "")
        s.save()
        self.log_action("Updated Theme Settings")
        messages.success(request, "Theme settings saved.")
        return redirect("theme_settings")
