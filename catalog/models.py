from django.db import models
from django.utils.text import slugify


DESIGN_TYPE_CHOICES = [
    ("Wood", "Wood"), ("Stone", "Stone"), ("Fabric", "Fabric"),
    ("Solid", "Solid"), ("Metallic", "Metallic"),
]

COLOR_CHOICES = [
    (c, c) for c in [
        "White", "Beige", "Black", "Blue", "Brown", "Green", "Grey",
        "Metallic", "Multicolor", "Orange", "Pink", "Purple", "Red", "Yellow",
    ]
]

BADGE_CHOICES = [
    ("", "None"), ("New", "New"), ("Bestseller", "Bestseller"), ("Limited", "Limited"),
]


class Category(models.Model):
    STATUS_DRAFT     = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES   = [(STATUS_DRAFT, "Draft"), (STATUS_PUBLISHED, "Published")]

    MEGA_GROUP_NONE     = "none"
    MEGA_GROUP_FINISHES = "finishes"
    MEGA_GROUP_PANELS   = "panels"
    MEGA_GROUP_CHOICES  = [
        ("none",     "Not in mega menu"),
        ("finishes", "Surface Finishes column"),
        ("panels",   "Panels & Décor column"),
    ]

    name             = models.CharField(max_length=255)
    slug             = models.SlugField(unique=True, blank=True)
    description      = models.TextField(blank=True)
    banner_image     = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="category_banners",
    )
    # Listing-page hero (shown at the top of /laminates, /louvers, /asa-sheets)
    hero_eyebrow     = models.CharField(
        max_length=120, blank=True,
        help_text='Small label above the title on the category listing page (e.g. "Surface Collection")',
    )
    hero_image_url   = models.CharField(
        max_length=500, blank=True,
        help_text="Hero background image URL. Overrides the banner image when set.",
    )
    # Mega-menu fields
    mega_group       = models.CharField(max_length=10, choices=MEGA_GROUP_CHOICES, default="none",
                                        help_text="Which column in the header mega menu this category appears in")
    mega_icon        = models.CharField(max_length=10, blank=True, default="◈",
                                        help_text="Single Unicode/emoji character shown in the mega menu")
    mega_description = models.CharField(max_length=120, blank=True,
                                        help_text="Short description shown under the category name in the mega menu")
    mega_position    = models.PositiveSmallIntegerField(default=0,
                                        help_text="Order within the mega menu column (lower = first)")
    # SEO
    seo_title        = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(max_length=320, blank=True)
    meta_keywords    = models.CharField(max_length=500, blank=True)
    og_image         = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="category_og_images",
    )
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created          = models.DateTimeField(auto_now_add=True)
    updated          = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Collection(models.Model):
    STATUS_DRAFT     = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES   = [(STATUS_DRAFT, "Draft"), (STATUS_PUBLISHED, "Published")]

    name                = models.CharField(max_length=255)
    slug                = models.SlugField(unique=True, blank=True)
    description         = models.TextField(blank=True)
    images              = models.ManyToManyField(
        "media_library.MediaAsset", blank=True, related_name="collections"
    )
    # Mega-menu fields
    show_in_mega_menu   = models.BooleanField(default=False,
                            help_text="Show this collection in the header mega menu collections grid")
    mega_accent_color   = models.CharField(max_length=7, blank=True, default="#7B9EC4",
                            help_text="Hex colour for the accent dot in the mega menu (e.g. #7B9EC4)")
    mega_position       = models.PositiveSmallIntegerField(default=0,
                            help_text="Order in the mega menu grid (lower = first)")
    # SEO
    seo_title           = models.CharField(max_length=255, blank=True)
    meta_description    = models.TextField(max_length=320, blank=True)
    meta_keywords       = models.CharField(max_length=500, blank=True)
    og_image            = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="collection_og_images",
    )
    status              = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created             = models.DateTimeField(auto_now_add=True)
    updated             = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product  = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="product_images")
    asset    = models.ForeignKey("media_library.MediaAsset", on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]


class Product(models.Model):
    STATUS_DRAFT     = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES   = [(STATUS_DRAFT, "Draft"), (STATUS_PUBLISHED, "Published")]

    name             = models.CharField(max_length=255)
    sku              = models.CharField(max_length=100, unique=True)
    slug             = models.SlugField(unique=True, blank=True)
    category         = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    collection       = models.ForeignKey(
        Collection, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="products",
    )
    short_description = models.CharField(
        max_length=300, blank=True,
        help_text="One-line summary shown on product cards and quick-view modal (max 300 chars)"
    )
    description      = models.TextField(blank=True)  # rendered by CKEditor
    features         = models.JSONField(default=list, blank=True)   # ["Feature 1", ...]
    tech_specs       = models.JSONField(default=dict, blank=True)   # {"Thickness": "1mm", ...}

    # Surface attributes — used by the storefront cards, filters and detail page
    finish           = models.CharField(max_length=60, blank=True,
                                        help_text='e.g. "High Gloss", "Ultra Matte", "Suede"')
    thickness        = models.CharField(max_length=40, blank=True, help_text='e.g. "1.0mm"')
    dimensions       = models.CharField(max_length=80, blank=True,
                                        help_text='e.g. "8ft × 4ft (2440 × 1220mm)"')
    surface          = models.CharField(max_length=80, blank=True,
                                        help_text='e.g. "Decorative Laminate"')
    application      = models.CharField(max_length=200, blank=True,
                                        help_text='Comma-separated uses, e.g. "Cabinets, Wardrobes, Wall Panels"')
    design_type      = models.CharField(max_length=20, blank=True, choices=DESIGN_TYPE_CHOICES)
    color            = models.CharField(max_length=20, blank=True, choices=COLOR_CHOICES)
    badge            = models.CharField(max_length=12, blank=True, choices=BADGE_CHOICES)
    accent_color     = models.CharField(max_length=7, blank=True, default="#85addc",
                                        help_text="Hex accent colour for this product's card")
    images           = models.ManyToManyField(
        "media_library.MediaAsset",
        through="ProductImage", blank=True, related_name="products",
    )
    image_urls       = models.JSONField(
        default=list, blank=True,
        help_text="External image URLs — used when no Media Library images are attached.",
    )
    pdf_catalog      = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="product_pdfs",
    )
    meta_title       = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(max_length=320, blank=True)
    meta_keywords    = models.CharField(max_length=500, blank=True)
    og_image         = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="product_og_images",
    )
    related_products = models.ManyToManyField("self", blank=True, symmetrical=True)
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created          = models.DateTimeField(auto_now_add=True)
    updated          = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def primary_image(self):
        pi = self.product_images.first()
        return pi.asset if pi else None
