from django.db import models
from django.utils.text import slugify


class BlogCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Blog Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    STATUS_DRAFT     = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES   = [(STATUS_DRAFT, "Draft"), (STATUS_PUBLISHED, "Published")]

    LAYOUT_FULL    = "full"
    LAYOUT_SIDEBAR = "sidebar"
    LAYOUT_CHOICES = [
        (LAYOUT_SIDEBAR, "Content + right sidebar"),
        (LAYOUT_FULL,    "Full width (no sidebar)"),
    ]

    title             = models.CharField(max_length=300)
    slug              = models.SlugField(max_length=300, unique=True, blank=True)
    layout            = models.CharField(
        max_length=12, choices=LAYOUT_CHOICES, default=LAYOUT_SIDEBAR,
        help_text="Public article layout. Sidebar shows author / categories / tags.",
    )
    featured_image    = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="blog_posts",
    )
    featured_image_url = models.URLField(
        max_length=500, blank=True,
        help_text="External banner / featured image URL. Used when no Media Library image is set.",
    )
    show_author       = models.BooleanField(
        default=True, help_text="Show the author card in the sidebar.",
    )
    show_share        = models.BooleanField(
        default=True, help_text="Show social share buttons (Facebook, WhatsApp, email…) in the sidebar.",
    )
    show_related      = models.BooleanField(
        default=True, help_text="Show the 'Recommended articles' section at the end of the post.",
    )
    content           = models.TextField(blank=True)  # CKEditor
    categories        = models.ManyToManyField(BlogCategory, blank=True, related_name="posts")
    tags              = models.ManyToManyField(Tag, blank=True, related_name="posts")
    author            = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="blog_posts",
    )
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    seo_title         = models.CharField(max_length=255, blank=True)
    meta_description  = models.TextField(max_length=320, blank=True)
    meta_keywords     = models.CharField(max_length=500, blank=True)
    og_image          = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="blog_og_images",
    )
    auto_faq_schema   = models.BooleanField(default=False)
    published_at      = models.DateTimeField(null=True, blank=True)
    created           = models.DateTimeField(auto_now_add=True)
    updated           = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
