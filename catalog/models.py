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


class ProductAttributeOption(models.Model):
    """Admin-managed values for a Product dropdown field (Design Type, Colour,
    Badge, Finish). Replaces the old hardcoded choice tuples above so the CMS
    can add/remove/reorder options without a code change."""

    DESIGN_TYPE = "design_type"
    COLOR       = "color"
    BADGE       = "badge"
    FINISH      = "finish"
    ATTRIBUTE_CHOICES = [
        (DESIGN_TYPE, "Design Type"),
        (COLOR,       "Colour"),
        (BADGE,       "Badge"),
        (FINISH,      "Finish"),
    ]

    attribute = models.CharField(max_length=20, choices=ATTRIBUTE_CHOICES)
    value     = models.CharField(max_length=60)
    position  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["attribute", "position", "id"]
        unique_together = [("attribute", "value")]

    def __str__(self):
        return f"{self.get_attribute_display()}: {self.value}"


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
    pdf_catalog         = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="collection_pdfs",
        help_text="Catalogue PDF for this collection, shown as a download on its product listing pages.",
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
    ROLE_GALLERY     = "gallery"
    ROLE_APPLICATION = "application"
    ROLE_TEXTURE     = "texture"
    ROLE_CHOICES = [
        (ROLE_GALLERY,     "Gallery"),
        (ROLE_APPLICATION, "Application"),
        (ROLE_TEXTURE,     "Texture"),
    ]

    product  = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="product_images")
    asset    = models.ForeignKey("media_library.MediaAsset", on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    role     = models.CharField(max_length=12, choices=ROLE_CHOICES, default=ROLE_GALLERY,
                                help_text="Where this image is shown on the product page: the main "
                                          "swatch/gallery, the single applied-in-a-room shot below the "
                                          "title, or a texture-variant thumbnail.")
    label    = models.CharField(max_length=60, blank=True,
                                help_text='Texture name shown under the thumbnail, e.g. "Fluted", '
                                          '"Glossy" — only used for the Texture role.')

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
    product_type     = models.CharField(max_length=80, blank=True,
                                        help_text='Shown as a tag and in the specs table, e.g. "Premium Laminate (1mm)", "PVC Panel", "Decorative Panel"')
    surface_category = models.CharField(max_length=80, blank=True,
                                        help_text='Shown as a tag and in the specs table, e.g. "Glossy Surface", "Matt Surface", "Architectural Panel"')
    application      = models.CharField(max_length=200, blank=True,
                                        help_text='Comma-separated uses, e.g. "Cabinets, Wardrobes, Wall Panels"')
    design_type      = models.CharField(max_length=20, blank=True, choices=DESIGN_TYPE_CHOICES)
    color            = models.CharField(max_length=20, blank=True, choices=COLOR_CHOICES)

    # Per-field visibility on the product detail page — lets the admin hide a
    # field there even when it has a value, without clearing the data itself.
    # A blank value always hides the row regardless of these flags.
    show_surface          = models.BooleanField(default=True, help_text="Show the “Design / Surface” row")
    show_product_type     = models.BooleanField(default=True, help_text="Show the “Product Type” tag & row")
    show_finish            = models.BooleanField(default=True, help_text="Show the “Finish / Texture” row")
    show_surface_category = models.BooleanField(default=True, help_text="Show the “Surface Category” tag & row")
    show_thickness         = models.BooleanField(default=True, help_text="Show the “Thickness” row")
    show_dimensions         = models.BooleanField(default=True, help_text="Show the “Standard Size” row")
    show_application         = models.BooleanField(default=True, help_text="Show the “Applications” row")
    show_design_type         = models.BooleanField(default=True, help_text="Show the “Design” tag")
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
    application_image_url = models.CharField(
        max_length=500, blank=True,
        help_text="External 'applied in a room' image URL — used when no Media Library "
                  "application image is attached. Shown below the title on the product page.",
    )
    texture_variants = models.JSONField(
        default=list, blank=True,
        help_text='External texture-variant thumbnails — [{"label": "Fluted", "image_url": "https://…"}, …]. '
                  "Used when no Media Library texture images are attached.",
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
        pi = self.product_images.filter(role=ProductImage.ROLE_GALLERY).first()
        return pi.asset if pi else None
