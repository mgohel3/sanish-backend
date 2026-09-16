from django.db import models

# ─────────────────────────────────────────────────────────────────────────────
# The REAL /applications page — a catalogue-of-photos gallery (S'Shades,
# Thre3, Cool Colour, Perspective V4, Thermo Laminates) that used to be
# entirely disk-driven: someone drops files into
# `sanish-next-fixed/public/assets/img/gallery/<slug>/` and a build script
# scans the folder into a manifest. This app makes that CMS-manageable
# without losing anything already uploaded — a seed migration imports every
# existing image (346 across 5 catalogues) as real rows pointing at their
# existing file paths, so nothing already there gets lost or re-uploaded.
#
# Not to be confused with the ``applications`` app (Kitchens/Commercial/
# Retail/… case-study categories) — a different, currently-unlinked feature
# on /applications/[category]. This ``gallery`` app is what actually powers
# the live /applications index and /applications/gallery/<catalogue> pages.
# ─────────────────────────────────────────────────────────────────────────────


class GalleryCatalogue(models.Model):
    slug = models.SlugField(max_length=60, unique=True)
    label = models.CharField(max_length=80)
    cover_image = models.CharField(max_length=500, blank=True, help_text="Card thumbnail on /applications.")
    position = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.label


class GalleryImage(models.Model):
    catalogue = models.ForeignKey(GalleryCatalogue, on_delete=models.CASCADE, related_name="images")
    image = models.CharField(max_length=500)
    product_id = models.CharField(
        max_length=40, blank=True,
        help_text='Laminate code shown to visitors, e.g. "6005-5". Leave blank to auto-number.',
    )
    position = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.catalogue.slug} · {self.product_id or self.pk}"
