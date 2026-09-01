from django.db import models


class SiteSettings(models.Model):
    """Singleton — always use SiteSettings.get(). Controls logo, contact, social, map, header/footer copy."""

    # ── Brand ─────────────────────────────────────────────────────────────────
    site_name        = models.CharField(max_length=100, default="Sanish Laminates")
    tagline          = models.CharField(max_length=200, blank=True, default="Premium Decorative Surface Solutions")
    logo_dark_url    = models.CharField(max_length=500, blank=True, default="/assets/img/logo/black-logo.svg",
                                         help_text="Path or URL for dark/black logo (used on light backgrounds)")
    logo_light_url   = models.CharField(max_length=500, blank=True, default="/assets/img/logo/footer-black-logo.svg",
                                         help_text="Path or URL for light logo (used on dark backgrounds / footer)")
    favicon_url      = models.CharField(max_length=500, blank=True, default="/favicon.ico")

    # ── Contact ───────────────────────────────────────────────────────────────
    phone_primary    = models.CharField(max_length=30, blank=True, default="+91 7027 777 032")
    phone_secondary  = models.CharField(max_length=30, blank=True)
    email_primary    = models.EmailField(blank=True, default="info@sanishlaminate.com")
    email_secondary  = models.EmailField(blank=True)
    address_line1    = models.CharField(max_length=200, blank=True)
    address_line2    = models.CharField(max_length=200, blank=True)
    city             = models.CharField(max_length=80, blank=True)
    state            = models.CharField(max_length=80, blank=True)
    pincode          = models.CharField(max_length=10, blank=True)
    working_hours    = models.CharField(max_length=100, blank=True, default="Mon–Sat: 9 AM – 6 PM")

    # ── Map ───────────────────────────────────────────────────────────────────
    map_embed_url    = models.TextField(blank=True, help_text="Full Google Maps embed iframe src URL")
    map_lat          = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    map_lng          = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # ── Social Media ──────────────────────────────────────────────────────────
    instagram_url    = models.URLField(blank=True)
    facebook_url     = models.URLField(blank=True)
    youtube_url      = models.URLField(blank=True)
    pinterest_url    = models.URLField(blank=True)
    linkedin_url     = models.URLField(blank=True)
    twitter_url      = models.URLField(blank=True)
    whatsapp_number  = models.CharField(max_length=20, blank=True, default="+917027777032",
                                         help_text="With country code, no spaces e.g. +917027777032")

    # ── Header / Top-bar ──────────────────────────────────────────────────────
    topbar_badge     = models.CharField(max_length=100, blank=True, default="Premium Surface Manufacturing")
    header_cta_label = models.CharField(max_length=60, blank=True, default="Download Catalogue")
    header_cta_url   = models.CharField(max_length=300, blank=True, default="#")

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_description = models.TextField(blank=True,
        default="Crafting elegant laminate and decorative surface solutions for architects, interior designers, commercial projects, and modern living spaces across India.")
    footer_copyright   = models.CharField(max_length=200, blank=True, default="© 2026 SANISH Laminate. All Rights Reserved.")
    footer_newsletter_text = models.CharField(max_length=300, blank=True,
        default="Subscribe for new collections, design inspiration, and exclusive dealer offers.")

    # ── Email / SMTP ──────────────────────────────────────────────────────────
    smtp_host          = models.CharField(max_length=255, blank=True,
                                           help_text="e.g. smtp.gmail.com. Leave blank to use the server's env-configured mail settings.")
    smtp_port          = models.PositiveIntegerField(default=587)
    smtp_username      = models.CharField(max_length=255, blank=True)
    smtp_password      = models.CharField(max_length=255, blank=True,
                                           help_text="For Gmail, use an App Password — not your normal account password.")
    smtp_use_tls       = models.BooleanField(default=True)
    smtp_from_email    = models.EmailField(blank=True, default="no-reply@sanishlaminate.com")
    smtp_notify_emails = models.CharField(max_length=500, blank=True,
                                           default="info@sanishlaminate.com,karyaweb2025@gmail.com",
                                           help_text="Comma-separated — who receives a notification on every new website form/popup submission.")

    class Meta:
        verbose_name        = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def full_address(self):
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.pincode]
        return ", ".join(p for p in parts if p)

    def notify_email_list(self):
        return [e.strip() for e in self.smtp_notify_emails.split(",") if e.strip()]

    def get_email_connection(self):
        """Returns an SMTP connection built from panel-configured settings, or None
        to signal the caller should fall back to the server's default EMAIL_BACKEND."""
        if not self.smtp_host:
            return None
        from django.core.mail import get_connection
        return get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_username,
            password=self.smtp_password,
            use_tls=self.smtp_use_tls,
            timeout=10,
        )


class GlobalSEO(models.Model):
    """Singleton — always use GlobalSEO.get()."""
    site_meta_title       = models.CharField(max_length=255, blank=True)
    site_meta_description = models.TextField(max_length=320, blank=True)
    site_keywords         = models.CharField(max_length=500, blank=True)
    robots_txt            = models.TextField(
        blank=True,
        default="User-agent: *\nAllow: /\nSitemap: https://api.sanishlaminate.com/sitemap.xml",
    )
    ga4_code              = models.CharField(max_length=50, blank=True, help_text="G-XXXXXXXXXX")
    gtm_code              = models.CharField(max_length=50, blank=True, help_text="GTM-XXXXXXX")
    fb_pixel_code         = models.CharField(max_length=50, blank=True)
    clarity_code          = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name        = "Global SEO Settings"
        verbose_name_plural = "Global SEO Settings"

    def __str__(self):
        return "Global SEO Settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Redirect(models.Model):
    TYPE_CHOICES = [("301", "301 Permanent"), ("302", "302 Temporary")]

    source_path      = models.CharField(max_length=500, unique=True)
    destination_path = models.CharField(max_length=500)
    type             = models.CharField(max_length=3, choices=TYPE_CHOICES, default="301")
    active           = models.BooleanField(default=True)
    created          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["source_path"]

    def __str__(self):
        return f"{self.source_path} → {self.destination_path} ({self.type})"


class NavLink(models.Model):
    """Editable navigation links for header, footer, mega-menu quick bar."""

    GROUP_MAIN        = "main"
    GROUP_TOPBAR      = "topbar"
    GROUP_MEGA_QUICK  = "mega_quick"
    GROUP_FOOTER_CO   = "footer_company"
    GROUP_CHOICES = [
        ("main",           "Main Navigation (desktop nav bar)"),
        ("topbar",         "Top Bar (above the header)"),
        ("mega_quick",     "Mega Menu — Bottom Quick Links"),
        ("footer_company", "Footer — Company column"),
    ]

    label        = models.CharField(max_length=80)
    url          = models.CharField(max_length=300, help_text="Relative (/about-us) or absolute URL")
    open_new_tab = models.BooleanField(default=False)
    group        = models.CharField(max_length=20, choices=GROUP_CHOICES, default="main")
    position     = models.PositiveSmallIntegerField(default=0, help_text="Lower = appears first")
    active       = models.BooleanField(default=True)

    class Meta:
        ordering = ["group", "position"]

    def __str__(self):
        return f"[{self.get_group_display()}] {self.label}"
