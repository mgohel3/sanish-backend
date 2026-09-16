"""
Bind Media Library assets that are ALREADY imported (sitting in their
collection's folder, e.g. "Cool Colours", "Perspective V4") to the matching
Product by shade code — no re-upload, no new files written.

Many products were created (via import_design_lists / CSV import) after their
photos had already been resized into the Media Library, so the ProductImage
join rows were never created. This command closes that gap by matching the
numeric shade code embedded in each asset's filename against Product.sku.

Only touches products that currently have zero ProductImage rows — never
overwrites or removes an existing binding.

Usage:
    python manage.py bind_existing_media --dry-run
    python manage.py bind_existing_media
"""
import re

from django.core.management.base import BaseCommand
from django.db.models import Count

from catalog.models import Collection, Product, ProductImage
from media_library.models import MediaAsset, MediaFolder

CODE_RE = re.compile(r"^(\d+(?:-\d+)?)")

# (MediaFolder name, Collection slug) for ranges stored as <code>.webp /
# <code>-preview.webp under a single folder.
FOLDER_COLLECTIONS = [
    ("Cool Colours", "cool-colour"),
    ("Perspective V4", "perspective-v4"),
    ("S'Shades", "sshades"),
    ("Thermo ASA", "thermo-asa"),
]


class Command(BaseCommand):
    help = "Bind already-imported Media Library assets to matching products by shade code."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        dry = opts["dry_run"]
        total_bound = 0

        for folder_name, coll_slug in FOLDER_COLLECTIONS:
            total_bound += self._bind_folder_range(folder_name, coll_slug, dry)

        total_bound += self._bind_thre3(dry)

        verb = "Would bind" if dry else "Bound"
        self.stdout.write(self.style.SUCCESS(f"{verb} images for {total_bound} product(s) total."))

    # ── code.webp / code-preview.webp ranges ───────────────────────────────

    def _bind_folder_range(self, folder_name, coll_slug, dry):
        folder = MediaFolder.objects.filter(name=folder_name).first()
        collection = Collection.objects.filter(slug=coll_slug).first()
        if not folder or not collection:
            self.stdout.write(self.style.WARNING(f"Skip {coll_slug}: folder or collection missing"))
            return 0

        by_code = {}
        for a in MediaAsset.objects.filter(folder=folder):
            fname = a.file.name.rsplit("/", 1)[-1]
            base = fname.rsplit(".", 1)[0]
            is_preview = base.lower().endswith("-preview")
            code = base[: -len("-preview")] if is_preview else base
            slot = by_code.setdefault(code, {})
            slot["preview" if is_preview else "main"] = a

        products = (Product.objects.filter(collection=collection)
                    .annotate(n=Count("product_images")).filter(n=0))
        bound = 0
        for p in products:
            m = CODE_RE.match(p.sku)
            if not m:
                continue
            imgs = by_code.get(m.group(1))
            if not imgs:
                continue
            if not dry:
                if "main" in imgs:
                    ProductImage.objects.create(product=p, asset=imgs["main"], position=0, role="gallery")
                if "preview" in imgs:
                    ProductImage.objects.create(product=p, asset=imgs["preview"], position=1, role="application")
            bound += 1
        self.stdout.write(f"{coll_slug}: bound {bound}/{products.count()} product(s) missing images")
        return bound

    # ── Thre3: exact "<code> <finish>" match, then raw-gallery fallback ────

    def _bind_thre3(self, dry):
        thre3 = Collection.objects.filter(slug="thre3").first()
        if not thre3:
            return 0

        bound_total = 0

        textures_folder = MediaFolder.objects.filter(name="Thre3 Textures").first()
        tex_by_key = {}
        if textures_folder:
            for a in MediaAsset.objects.filter(folder=textures_folder):
                fname = a.file.name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                m = re.match(r"^(\d+)\s*([A-Za-z]+)$", fname.strip())
                if m:
                    tex_by_key[f"{m.group(1)} {m.group(2).upper()}"] = a

        products = (Product.objects.filter(collection=thre3)
                    .annotate(n=Count("product_images")).filter(n=0))
        bound = 0
        for p in products:
            asset = tex_by_key.get(p.sku.strip().upper())
            if not asset:
                continue
            if not dry:
                ProductImage.objects.create(product=p, asset=asset, position=0, role="gallery")
            bound += 1
        self.stdout.write(f"thre3 (exact texture match): bound {bound}/{products.count()} product(s)")
        bound_total += bound

        # Fallback: raw un-resized gallery scans, matched by leading code only
        # (same physical shade, finish-agnostic room-applied shot).
        gal_by_code = {}
        for a in MediaAsset.objects.filter(file__istartswith="imported/img/gallery/thre3/"):
            fname = a.file.name.rsplit("/", 1)[-1]
            m = CODE_RE.match(fname)
            if not m:
                continue
            code = m.group(1)
            slot = gal_by_code.setdefault(code, {})
            if "_pw" in fname.lower():
                slot["preview"] = a
            slot.setdefault("main", a)

        products2 = (Product.objects.filter(collection=thre3)
                     .annotate(n=Count("product_images")).filter(n=0))
        bound2 = 0
        for p in products2:
            m = CODE_RE.match(p.sku)
            if not m:
                continue
            imgs = gal_by_code.get(m.group(1))
            if not imgs:
                continue
            if not dry:
                ProductImage.objects.create(
                    product=p, asset=imgs.get("preview", imgs["main"]), position=0, role="gallery")
            bound2 += 1
        self.stdout.write(f"thre3 (raw gallery fallback): bound {bound2}/{products2.count()} product(s)")
        return bound_total + bound2
