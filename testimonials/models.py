from django.db import models

# ─────────────────────────────────────────────────────────────────────────────
# Carpenter testimonials — the CMS-managed carousel on /rewards, between the
# "What You Get" benefits grid and the FAQ section. Sanish's own team adds,
# hides or removes entries here over time as real carpenter feedback comes
# in (2026-10-01 request) — same is_active/position pattern as faq.Faq, so a
# hidden entry stays in the list for later rather than being lost.
# ─────────────────────────────────────────────────────────────────────────────


class CarpenterTestimonial(models.Model):
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
    position = models.PositiveSmallIntegerField(default=0, help_text="Lower = appears first.")
    is_active = models.BooleanField(
        default=True, help_text="Inactive entries are hidden from the live site without deleting them.",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Carpenter Testimonial"

    def __str__(self):
        return self.name
