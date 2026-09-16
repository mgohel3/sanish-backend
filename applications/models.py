from django.db import models

# ─────────────────────────────────────────────────────────────────────────────
# CMS management for the "Applications" (use-case) pages — /applications and
# /applications/<category>. Mirrors the shape of the hard-coded
# `CATEGORIES` / `applications` arrays in the frontend's
# `src/lib/applications.ts`, so seeding from that data is lossless. Modeled
# after `catalog` (Product/Category) — the same list/CRUD pattern, since the
# client asked for "application page management... like products".
# ─────────────────────────────────────────────────────────────────────────────


class ApplicationCategory(models.Model):
    slug = models.SlugField(max_length=60, unique=True)
    label = models.CharField(max_length=80)
    description = models.CharField(max_length=500, blank=True)
    accent = models.CharField(max_length=7, blank=True, help_text="Hex accent colour, e.g. #85addc")
    image = models.CharField(max_length=500, blank=True, help_text="Hero image for the category banner.")
    # Each: {"image": "...", "caption": "..."} — the simple photo gallery shown
    # for this category, uploaded straight from the CMS (Media Library:
    # upload / browse / paste a link). This is the primary way this app is
    # actually used day-to-day, separate from the more detailed Case Studies.
    gallery = models.JSONField(default=list, blank=True)
    position = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name_plural = "Application Categories"

    def __str__(self):
        return self.label


class ApplicationProject(models.Model):
    """One case study shown in a category's project gallery."""

    slug = models.SlugField(max_length=100, unique=True)
    label = models.CharField(max_length=150)
    category = models.ForeignKey(
        ApplicationCategory, on_delete=models.CASCADE, related_name="projects"
    )
    finish = models.CharField(max_length=150, blank=True)
    image = models.CharField(max_length=500, blank=True, help_text="Hero / cover image.")
    tall = models.BooleanField(default=False, help_text="Layout hint for the masonry grid.")
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    year = models.CharField(max_length=10, blank=True)
    designer = models.CharField(max_length=150, blank=True)
    area = models.CharField(max_length=100, blank=True)

    # Each: {"image": "..."}
    gallery = models.JSONField(default=list, blank=True)
    # Each: {"text": "..."}
    highlights = models.JSONField(default=list, blank=True)
    # Each: {"name","code","collection","finish","usage","product_slug"}
    products = models.JSONField(default=list, blank=True)

    position = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.category.label} · {self.label}"
