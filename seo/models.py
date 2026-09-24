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
    header_cta_url   = models.CharField(max_length=300, blank=True, default="/collection",
                                          help_text="Where the header's CTA button links to, e.g. /collection or a full URL")

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


class ThemeSettings(models.Model):
    """Singleton — always use ThemeSettings.get(). Controls site-wide colors, typography,
    button styles and layout tokens served to the frontend (WordPress-Customizer style)."""

    FONT_CHOICES = [
        ("Heebo",            "Heebo — current body/UI font"),
        ("Bodoni Moda",      "Bodoni Moda — current heading font (fallback for the licensed “Vogue” display face)"),
        ("Inter",            "Inter"),
        ("Roboto",           "Roboto"),
        ("Poppins",          "Poppins"),
        ("Montserrat",       "Montserrat"),
        ("Open Sans",        "Open Sans"),
        ("Lato",             "Lato"),
        ("Nunito",           "Nunito"),
        ("Playfair Display", "Playfair Display"),
        ("Raleway",          "Raleway"),
        ("Work Sans",        "Work Sans"),
        ("Mulish",           "Mulish"),
        ("DM Sans",          "DM Sans"),
        ("Manrope",          "Manrope"),
        ("Outfit",           "Outfit"),
        ("Sora",             "Sora"),
        ("Space Grotesk",    "Space Grotesk"),
    ]
    BASE_FONT_SIZE_CHOICES = [
        ("14px", "Small (14px)"),
        ("15px", "Default (15px)"),
        ("16px", "Large (16px)"),
        ("18px", "Extra Large (18px)"),
    ]
    BUTTON_STYLE_CHOICES = [
        ("solid",   "Solid"),
        ("outline", "Outline"),
        ("ghost",   "Ghost (text only)"),
        ("soft",    "Soft (tinted)"),
    ]
    BUTTON_RADIUS_CHOICES = [
        ("0px",     "Square"),
        ("4px",     "Small"),
        ("8px",     "Medium"),
        ("12px",    "Large"),
        ("9999px",  "Pill — current site style"),
    ]
    BUTTON_HOVER_CHOICES = [
        ("swap",    "Swap to accent color — current site style"),
        ("darken",  "Darken"),
        ("lighten", "Lighten"),
        ("scale",   "Scale up"),
        ("none",    "None"),
    ]
    CONTAINER_WIDTH_CHOICES = [
        ("1120px", "Narrow (1120px)"),
        ("1280px", "Wide (1280px)"),
        ("1400px", "Default (1400px) — current site width"),
        ("1600px", "Extra Wide (1600px)"),
    ]
    RADIUS_CHOICES = [
        ("0px",  "None"),
        ("6px",  "Small"),
        ("12px", "Medium"),
        ("20px", "Large — current site style"),
        ("28px", "Extra Large"),
    ]
    SHADOW_CHOICES = [
        ("none",   "None"),
        ("soft",   "Soft"),
        ("medium", "Medium"),
        ("strong", "Strong"),
    ]

    # ── Colors ────────────────────────────────────────────────────────────────
    # Defaults mirror the live "Approved Sanish Palette" (sanish-next-fixed/design.md)
    # and the current computed values in sanish-next-fixed/src/app/globals.css.
    primary_color      = models.CharField(max_length=7, default="#AC8CC0", help_text="Main brand color — buttons, links, CTAs and the active-nav indicator")
    secondary_color     = models.CharField(max_length=7, default="#85ADDC", help_text="Sanish Blue — secondary brand color")
    accent_color        = models.CharField(max_length=7, default="#FABF7D", help_text="Sanish Apricot — badges, tags and small decorative highlights")
    heading_color       = models.CharField(max_length=7, default="#24262B")
    text_color          = models.CharField(max_length=7, default="#24262B")
    link_color          = models.CharField(max_length=7, default="#AC8CC0")
    link_hover_color    = models.CharField(max_length=7, default="#F39BA2", help_text="Sanish Pink — hover/focus/active state across the whole site")
    background_color    = models.CharField(max_length=7, default="#FAFAFA")
    header_bg_color     = models.CharField(max_length=7, default="#FFFFFF", help_text="Header is a translucent frosted-glass bar over white in production — this is its flat approximation")
    footer_bg_color     = models.CharField(max_length=7, default="#F3F4F6", help_text="Footer uses a soft pink→purple gradient fading into this color in production — this is its flat approximation")
    footer_text_color   = models.CharField(max_length=7, default="#686B72")

    # ── Typography ────────────────────────────────────────────────────────────
    heading_font        = models.CharField(max_length=40, choices=FONT_CHOICES, default="Bodoni Moda")
    body_font            = models.CharField(max_length=40, choices=FONT_CHOICES, default="Heebo")
    base_font_size       = models.CharField(max_length=10, choices=BASE_FONT_SIZE_CHOICES, default="15px")

    # ── Buttons ───────────────────────────────────────────────────────────────
    button_style         = models.CharField(max_length=10, choices=BUTTON_STYLE_CHOICES, default="solid")
    button_radius        = models.CharField(max_length=10, choices=BUTTON_RADIUS_CHOICES, default="9999px")
    button_hover_effect  = models.CharField(max_length=10, choices=BUTTON_HOVER_CHOICES, default="swap")
    button_text_color    = models.CharField(max_length=7, default="#FFFFFF", help_text="Text color on solid/soft buttons")

    # ── Layout ────────────────────────────────────────────────────────────────
    container_max_width  = models.CharField(max_length=10, choices=CONTAINER_WIDTH_CHOICES, default="1400px")
    border_radius         = models.CharField(max_length=10, choices=RADIUS_CHOICES, default="20px",
                                              help_text="Global corner radius for cards, inputs and images")
    card_shadow_style     = models.CharField(max_length=10, choices=SHADOW_CHOICES, default="soft")

    class Meta:
        verbose_name        = "Theme Settings"
        verbose_name_plural = "Theme Settings"

    def __str__(self):
        return "Theme Settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    # Fixed reference swatches — the 4 approved Sanish brand colors from
    # sanish-next-fixed/design.md. Shown as a read-only reference strip in the
    # CMS regardless of what the editable fields above are set to.
    approved_palette_swatches = [
        ("#85ADDC", "Blue"),
        ("#AC8CC0", "Purple"),
        ("#F39BA2", "Pink"),
        ("#FABF7D", "Apricot"),
    ]

    def as_css_vars(self):
        """Flat dict of CSS custom-property name -> value, for the frontend to inject."""
        return {
            "--theme-primary":        self.primary_color,
            "--theme-secondary":      self.secondary_color,
            "--theme-accent":         self.accent_color,
            "--theme-heading-color":  self.heading_color,
            "--theme-text-color":     self.text_color,
            "--theme-link-color":     self.link_color,
            "--theme-link-hover":     self.link_hover_color,
            "--theme-bg":             self.background_color,
            "--theme-header-bg":      self.header_bg_color,
            "--theme-footer-bg":      self.footer_bg_color,
            "--theme-footer-text":    self.footer_text_color,
            "--theme-heading-font":   self.heading_font,
            "--theme-body-font":      self.body_font,
            "--theme-base-font-size": self.base_font_size,
            "--theme-button-radius":  self.button_radius,
            "--theme-button-text":    self.button_text_color,
            "--theme-container-width": self.container_max_width,
            "--theme-radius":         self.border_radius,
        }


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
    clarity_code          = models.CharField(max_length=50, blank=True, help_text="Microsoft Clarity project ID, e.g. abcd1234ef")
    gsc_verification_code = models.CharField(max_length=100, blank=True,
        help_text="Google Search Console HTML tag verification content — from the 'content=\"...\"' value of the "
                   "meta tag Search Console gives you (HTML tag verification method), not the whole tag.")

    RECAPTCHA_OFF = "off"
    RECAPTCHA_V2  = "v2"
    RECAPTCHA_V3  = "v3"
    RECAPTCHA_VERSION_CHOICES = [
        (RECAPTCHA_OFF, "Off"),
        (RECAPTCHA_V2, "v2 (\"I'm not a robot\" checkbox)"),
        (RECAPTCHA_V3, "v3 (invisible, score-based)"),
    ]
    recaptcha_version    = models.CharField(max_length=3, choices=RECAPTCHA_VERSION_CHOICES, default=RECAPTCHA_OFF)
    recaptcha_site_key   = models.CharField(max_length=100, blank=True, help_text="reCAPTCHA site key (public).")
    recaptcha_secret_key = models.CharField(max_length=100, blank=True, help_text="reCAPTCHA secret key (server-side only, never exposed to the frontend).")
    recaptcha_v3_min_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.5,
        help_text="v3 only — submissions scoring below this (0.0-1.0, higher = more human) are rejected as spam.")

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
    """Deprecated: superseded by ``menus.Menu``/``MenuItem`` system menus.
    Kept only as historical data — no longer read or editable via the CMS
    or the public API."""

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
