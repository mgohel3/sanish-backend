import re
from django.db import models
from django.utils.text import slugify

from homepage import blocks as _blocks


SCHEMA_CHOICES = [
    ("LocalBusiness",  "Local Business"),
    ("Product",        "Product"),
    ("FAQPage",        "FAQ Page"),
    ("Organization",   "Organization"),
    ("Article",        "Article"),
    ("BreadcrumbList", "Breadcrumb List"),
]


def fill_placeholders(text, city="", state="", product=""):
    if not text:
        return text
    return (
        text
        .replace("{{city}}", city)
        .replace("{{state}}", state)
        .replace("{{product}}", product)
    )


def fill_placeholders_in_list(items, city="", state="", product=""):
    """Apply fill_placeholders to every string value inside a list of dicts (FAQs, why_choose_us, etc.)."""
    if not items:
        return items
    result = []
    for item in items:
        if isinstance(item, dict):
            result.append({
                k: fill_placeholders(v, city, state, product) if isinstance(v, str) else v
                for k, v in item.items()
            })
        elif isinstance(item, str):
            result.append(fill_placeholders(item, city, state, product))
        else:
            result.append(item)
    return result


class PageTemplate(models.Model):
    name                  = models.CharField(max_length=255)
    product_type_label    = models.CharField(max_length=100, help_text='e.g. "High Pressure Laminates"')
    url_pattern           = models.CharField(
        max_length=100,
        help_text='e.g. {product}-in-{city} — will be slugified',
        default="{product}-in-{city}",
    )
    # Default content — supports {{city}}, {{state}}, {{product}} placeholders
    default_h1            = models.CharField(max_length=255, blank=True)
    default_hero_heading  = models.CharField(max_length=255, blank=True)
    default_hero_desc     = models.TextField(blank=True)
    default_main_content  = models.TextField(blank=True)
    why_choose_us         = models.JSONField(default=list, blank=True)
    faqs                  = models.JSONField(default=list, blank=True)
    default_schema_type   = models.CharField(
        max_length=20, choices=SCHEMA_CHOICES, default="LocalBusiness"
    )
    related_products      = models.ManyToManyField(
        "catalog.Product", blank=True, related_name="page_templates"
    )
    gallery               = models.ManyToManyField(
        "media_library.MediaAsset", blank=True, related_name="page_templates"
    )
    created               = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def build_slug(self, city, state=""):
        slug_city    = slugify(city)
        slug_product = slugify(self.product_type_label)
        slug_state   = slugify(state)
        pattern = self.url_pattern
        result = (
            pattern
            .replace("{product}", slug_product)
            .replace("{city}",    slug_city)
            .replace("{state}",   slug_state)
        )
        return slugify(result)


class CityPage(models.Model):
    STATUS_DRAFT     = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES   = [(STATUS_DRAFT, "Draft"), (STATUS_PUBLISHED, "Published")]

    template         = models.ForeignKey(
        PageTemplate, on_delete=models.PROTECT, related_name="city_pages"
    )
    city             = models.CharField(max_length=100)
    state            = models.CharField(max_length=100, blank=True)
    slug             = models.SlugField(max_length=200, unique=True, blank=True)
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    # Per-page override fields (null = inherit from template)
    h1_title          = models.CharField(max_length=255, blank=True, null=True)
    hero_heading      = models.CharField(max_length=255, blank=True, null=True)
    hero_description  = models.TextField(blank=True, null=True)
    main_content      = models.TextField(blank=True, null=True)
    why_choose_us     = models.JSONField(null=True, blank=True)
    faqs              = models.JSONField(null=True, blank=True)
    related_products  = models.ManyToManyField(
        "catalog.Product", blank=True, related_name="city_pages"
    )
    gallery           = models.ManyToManyField(
        "media_library.MediaAsset", blank=True, related_name="city_pages"
    )
    testimonials      = models.JSONField(default=list, blank=True)

    # SEO block
    seo_title         = models.CharField(max_length=255, blank=True)
    meta_description  = models.TextField(max_length=320, blank=True)
    meta_keywords     = models.CharField(max_length=500, blank=True)
    canonical_url     = models.URLField(blank=True)
    og_title          = models.CharField(max_length=255, blank=True)
    og_description    = models.TextField(max_length=320, blank=True)
    og_image          = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="city_page_og",
    )
    twitter_title     = models.CharField(max_length=255, blank=True)
    twitter_description = models.TextField(max_length=280, blank=True)
    schema_type       = models.CharField(
        max_length=20, choices=SCHEMA_CHOICES, blank=True
    )

    created           = models.DateTimeField(auto_now_add=True)
    updated           = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["city"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.template.build_slug(self.city, self.state)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.template.product_type_label} in {self.city}"

    def resolved(self):
        """Returns merged template + override dict ready to be served by the API."""
        t = self.template
        city    = self.city
        state   = self.state
        product = t.product_type_label

        def resolve(override, default):
            if override is not None:
                return fill_placeholders(override, city, state, product)
            return fill_placeholders(default, city, state, product)

        return {
            "slug":             self.slug,
            "city":             city,
            "state":            state,
            "product_type":     product,
            "h1_title":         resolve(self.h1_title, t.default_h1),
            "hero_heading":     resolve(self.hero_heading, t.default_hero_heading),
            "hero_description": resolve(self.hero_description, t.default_hero_desc),
            "main_content":     resolve(self.main_content, t.default_main_content),
            "why_choose_us":    fill_placeholders_in_list(
                                    self.why_choose_us if self.why_choose_us is not None else t.why_choose_us,
                                    city, state, product,
                                ),
            "faqs":             fill_placeholders_in_list(
                                    self.faqs if self.faqs is not None else t.faqs,
                                    city, state, product,
                                ),
            "testimonials":     self.testimonials,
            "schema_type":      self.schema_type or t.default_schema_type,
            "seo": {
                "title":               self.seo_title,
                "meta_description":    self.meta_description,
                "meta_keywords":       self.meta_keywords,
                "canonical_url":       self.canonical_url,
                "og_title":            self.og_title,
                "og_description":      self.og_description,
                "og_image":            self.og_image.url if self.og_image else "",
                "twitter_title":       self.twitter_title,
                "twitter_description": self.twitter_description,
            },
        }


# ─────────────────────────────────────────────────────────────────────────────
# Generic CMS-managed site pages (Home, About, Contact, …)
#
# A ``SitePage`` owns an ordered list of ``PageSection`` blocks. The blocks use
# the exact same registry as the home page — ``homepage.blocks.BLOCK_TYPES`` —
# so the CMS form/list templates and the ``resolved()`` merge behave identically.
# ─────────────────────────────────────────────────────────────────────────────


class SitePage(models.Model):
    """One editable page of the public site."""

    slug        = models.SlugField(
        max_length=80, unique=True,
        help_text='Matches the CMS/API key, e.g. "about-us".',
    )
    title       = models.CharField(max_length=120)
    path        = models.CharField(
        max_length=120, blank=True,
        help_text='Front-end route for the "Preview" link, e.g. "/about-us".',
    )
    description = models.CharField(max_length=255, blank=True)
    position    = models.PositiveIntegerField(default=0)
    is_system   = models.BooleanField(
        default=True,
        help_text="System pages cannot be deleted from the CMS.",
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Unpublished (draft) pages return 404 on the live site.",
    )
    # A few pages have their block editor elsewhere (the Home page keeps its own
    # HomeSection-based editor). When set, the CMS list links straight to it.
    external_url_name = models.CharField(max_length=80, blank=True)

    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Site Page"

    def __str__(self):
        return self.title


class PageSection(models.Model):
    """One orderable block on a :class:`SitePage` — a per-page clone of
    ``homepage.models.HomeSection``."""

    page       = models.ForeignKey(
        SitePage, on_delete=models.CASCADE, related_name="sections"
    )
    block_type = models.CharField(max_length=40, choices=_blocks.block_choices())
    label      = models.CharField(
        max_length=120,
        help_text="Internal name shown in the CMS list (not published).",
    )
    anchor_id  = models.SlugField(
        max_length=60, blank=True,
        help_text='Optional id for the <section> tag (e.g. "team" -> /about-us#team).',
    )
    position   = models.PositiveIntegerField(default=0)
    enabled    = models.BooleanField(default=True)
    content    = models.JSONField(default=dict, blank=True)

    created    = models.DateTimeField(auto_now_add=True)
    updated    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Page Section"

    def __str__(self):
        return f"{self.page.slug} · {self.position:02d}. {self.label}"

    @property
    def block_config(self) -> dict:
        return _blocks.BLOCK_TYPES.get(self.block_type, {})

    def resolved(self) -> dict:
        """Stored content merged over the block type's defaults."""
        data = _blocks.defaults_for(self.block_type)
        if isinstance(self.content, dict):
            for key, value in self.content.items():
                if value in ("", None) and key in data:
                    continue  # keep the default rather than blanking it
                data[key] = value
        return data
