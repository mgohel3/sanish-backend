from django.db import models
from django.utils.text import slugify

# ─────────────────────────────────────────────────────────────────────────────
# Testimonials — CMS-managed carousels. Entries are grouped into editor-defined
# CATEGORIES (Carpenters, Clients, … add more any time); the "Client
# Testimonials" page block shows whichever category it is pointed at, so the
# same design can be dropped on any page with a different list each time.
# Same is_active/position pattern as faq.Faq, so a hidden entry stays in the
# list for later rather than being lost.
# ─────────────────────────────────────────────────────────────────────────────


class TestimonialCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    position = models.PositiveSmallIntegerField(default=0, help_text="Lower = appears first (tab order).")

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Testimonial Category"
        verbose_name_plural = "Testimonial Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "category"
            slug, n = base, 2
            while TestimonialCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CarpenterTestimonial(models.Model):
    # (Model name kept from the original Carpenters-only version so existing
    # data / migrations / API URLs are untouched — it now holds every category.)
    category = models.ForeignKey(
        TestimonialCategory, null=True, blank=True, on_delete=models.PROTECT,
        related_name="testimonials",
    )
    name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=150, blank=True,
        help_text='Shown under the name, e.g. "Carpenter, Mumbai". Leave blank to omit.',
    )
    quote = models.TextField(max_length=600)
    photo_url = models.CharField(
        max_length=500, blank=True,
        help_text="Optional (path or URL, same as other image fields). Falls back to the "
                   "carpenter's initials in a coloured circle when not set.",
    )
    proof_image_url = models.CharField(
        max_length=500, blank=True,
        help_text="Optional payment-proof screenshot (path or URL, picked from the Media Library). "
                   "Shown at the top of the card in place of the quote icon.",
    )
    position = models.PositiveSmallIntegerField(default=0, help_text="Lower = appears first.")
    is_active = models.BooleanField(
        default=True, help_text="Inactive entries are hidden from the live site without deleting them.",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Testimonial"

    def __str__(self):
        return self.name
