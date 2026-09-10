"""
Import a solid-shade laminate range from one of the client's delivery folders.

    <SOURCE>/FULLSHEETS/<code>_OK.jpg   -> main product image (flat sheet swatch)
    <SOURCE>/PREVIEW/<code>_PW.jpg      -> "applied" preview (shade in a room)

Every file is named by its numeric shade code; per the client the product NAME
and SKU are that bare code. Images are resized so their longest edge is
<= --max-edge px (aspect ratio preserved, never cropped), stored as WebP in the
Media Library, and attached as ProductImage rows (position 0 = full sheet,
position 1 = preview).

Idempotent: re-running updates products in place and reuses already-imported
media. Generalised from the one-off `import_cool_colors` command.

Example:
    python manage.py import_sheet_range \
        --source "F:/.../SANISH 0.8 (Perspective)" \
        --collection perspective-v4 --thickness 0.8mm --draft-collection-extras
"""
import re
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from PIL import Image, ImageOps

# Client full-sheet scans can be huge (some are 14400 x 30000 px). These are
# trusted local files, so lift Pillow's decompression-bomb guard.
Image.MAX_IMAGE_PIXELS = None

from catalog.models import Category, Collection, Product, ProductImage
from media_library.models import MediaAsset, MediaFolder

SHORT_DESC = (
    "A solid-shade decorative laminate from the Sanish {range} range (shade "
    "{code}) — an even, contemporary {thickness} surface that pairs easily with "
    "wood, metal and stone in modern interiors."
)

DESCRIPTION = (
    "<p>{code} is part of the Sanish <strong>{range}</strong> collection — a range "
    "of solid-shade decorative laminates for clean, cohesive interiors. The surface "
    "carries a smooth, even colour from edge to edge, so it reads consistently "
    "across large runs of shutters, wardrobe fronts and wall panelling.</p>"
    "<p>Like every Sanish laminate it is scratch resistant, moisture proof and easy "
    "to wipe clean — equally suited to kitchens, wardrobes, retail joinery and "
    "commercial fit-outs. Supplied in standard 8ft × 4ft (2440 × 1220 mm) sheets at "
    "{thickness} thickness.</p>"
    "<p>Shades in this range follow the factory shade code. For exact colour "
    "matching, request a physical sample or download the {range} catalogue from the "
    "catalogue page.</p>"
)

FEATURES = [
    "Scratch Resistant",
    "Moisture Proof",
    "Anti-Fingerprint",
    "Easy to Clean",
    "Fire Retardant",
]


class Command(BaseCommand):
    help = "Import a solid-shade laminate range (FULLSHEETS + PREVIEW folders)."

    def add_arguments(self, parser):
        parser.add_argument("--source", required=True,
                            help="Folder containing FULLSHEETS/ and PREVIEW/ subfolders")
        parser.add_argument("--collection", required=True,
                            help="Target Collection slug (must already exist)")
        parser.add_argument("--category", default="laminates",
                            help="Target Category slug (default: laminates)")
        parser.add_argument("--range-label", default="",
                            help="Range name used in copy + specs (default: the collection name)")
        parser.add_argument("--thickness", default="1.0mm")
        parser.add_argument("--surface", default="Decorative Laminate")
        parser.add_argument("--media-subdir", default="",
                            help="MEDIA_ROOT subdir for resized files (default: products/<collection-slug>)")
        parser.add_argument("--folder", default="",
                            help="Media Library folder name (default: the collection name)")
        parser.add_argument("--max-edge", type=int, default=2000,
                            help="Longest image edge in px after resize (aspect ratio kept)")
        parser.add_argument("--webp-quality", type=int, default=82)
        parser.add_argument("--draft-collection-extras", action="store_true",
                            help="Set any product already in this collection but NOT in the "
                                 "import set to draft")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        source = Path(opts["source"])
        fullsheet_dir = source / "FULLSHEETS"
        preview_dir   = source / "PREVIEW"
        if not fullsheet_dir.is_dir():
            raise CommandError(f"Not found: {fullsheet_dir}")

        try:
            category = Category.objects.get(slug=opts["category"])
        except Category.DoesNotExist:
            raise CommandError(f"Category '{opts['category']}' does not exist")
        try:
            collection = Collection.objects.get(slug=opts["collection"])
        except Collection.DoesNotExist:
            raise CommandError(f"Collection '{opts['collection']}' does not exist")

        range_label = opts["range_label"] or collection.name
        thickness   = opts["thickness"]
        surface     = opts["surface"]
        media_subdir = opts["media_subdir"] or f"products/{slugify(collection.name)}"
        folder_name  = opts["folder"] or collection.name
        folder, _ = MediaFolder.objects.get_or_create(name=folder_name)

        # code -> {"full": Path, "preview": Path|None}
        # Codes are numeric, optionally with a "-N" sub-code (e.g. 6005-5).
        exts = (".jpg", ".jpeg", ".png", ".gif", ".webp")
        code_re = re.compile(r"(\d+(?:-\d+)?)")
        items = {}
        for f in sorted(fullsheet_dir.iterdir()):
            m = code_re.match(f.name)
            if m and f.suffix.lower() in exts:
                items[m.group(1)] = {"full": f, "preview": None}
        if preview_dir.is_dir():
            for f in preview_dir.iterdir():
                m = code_re.match(f.name)
                if m and m.group(1) in items and f.suffix.lower() in exts:
                    cur = items[m.group(1)]["preview"]
                    if cur is None or "_PW" in f.name.upper():
                        items[m.group(1)]["preview"] = f

        codes = sorted(items)
        with_prev = sum(1 for c in codes if items[c]["preview"])
        self.stdout.write(f"{source.name}: {len(codes)} shades ({with_prev} with previews) "
                          f"-> collection '{collection.slug}', category '{category.slug}'")
        if opts["dry_run"]:
            for c in codes:
                self.stdout.write(f"  {c}  full={items[c]['full'].name}  "
                                  f"preview={items[c]['preview'].name if items[c]['preview'] else '-'}")
            return

        media_root = Path(settings.MEDIA_ROOT)
        (media_root / media_subdir).mkdir(parents=True, exist_ok=True)
        max_edge = opts["max_edge"]
        quality  = opts["webp_quality"]

        created = updated = 0
        with transaction.atomic():
            for code in codes:
                full_asset = self._asset_for(
                    items[code]["full"], f"{media_subdir}/{code}.webp",
                    title=code, alt=f"Sanish {range_label} laminate — shade {code}",
                    folder=folder, max_edge=max_edge, quality=quality,
                )
                preview_asset = None
                if items[code]["preview"]:
                    preview_asset = self._asset_for(
                        items[code]["preview"], f"{media_subdir}/{code}-preview.webp",
                        title=f"{code} — applied preview",
                        alt=f"Sanish {range_label} shade {code} applied to interior joinery",
                        folder=folder, max_edge=max_edge, quality=quality,
                    )

                product, is_new = Product.objects.get_or_create(
                    sku=code, defaults={"name": code, "category": category}
                )
                product.name             = code
                product.slug             = product.slug or ""
                product.category         = category
                product.collection       = collection
                product.status           = "published"
                product.short_description = SHORT_DESC.format(
                    range=range_label, code=code, thickness=thickness)
                product.description       = DESCRIPTION.format(
                    range=range_label, code=code, thickness=thickness)
                product.surface          = surface
                product.thickness        = thickness
                product.dimensions       = "8ft × 4ft (2440 × 1220mm)"
                product.application      = "Cabinets, Wardrobes, Wall Panels, Shutters, Interiors"
                product.design_type      = "Solid"
                product.features         = list(FEATURES)
                product.tech_specs       = {
                    "Thickness": thickness,
                    "Sheet Size": "2440mm × 1220mm (8ft × 4ft)",
                    "Surface": surface,
                    "Range": range_label,
                }
                if not product.accent_color:
                    product.accent_color = "#85addc"
                product.save()

                product.product_images.all().delete()
                ProductImage.objects.create(product=product, asset=full_asset, position=0)
                if preview_asset:
                    ProductImage.objects.create(product=product, asset=preview_asset, position=1)

                created += is_new
                updated += (not is_new)
                self.stdout.write(f"  [{'new' if is_new else 'upd'}] {code}"
                                  f"  ({'2 imgs' if preview_asset else '1 img'})")

            if opts["draft_collection_extras"]:
                extras = (Product.objects
                          .filter(collection=collection)
                          .exclude(sku__in=codes)
                          .exclude(status="draft"))
                n = extras.update(status="draft")
                if n:
                    self.stdout.write(self.style.WARNING(
                        f"Drafted {n} product(s) already in '{collection.slug}' but not in this range"))

        self.stdout.write(self.style.SUCCESS(
            f"Done — {created} created, {updated} updated, "
            f"{len(codes)} {range_label} products published."
        ))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _asset_for(self, src_path, rel_dest, *, title, alt, folder, max_edge, quality):
        """Resize src image (keep aspect, no crop), write WebP to MEDIA_ROOT/rel_dest,
        return a MediaAsset (reused if it already exists)."""
        media_root = Path(settings.MEDIA_ROOT)
        abs_dest = media_root / rel_dest

        if not abs_dest.exists():
            with Image.open(src_path) as im:
                im = ImageOps.exif_transpose(im)
                im = im.convert("RGB")
                if max(im.size) > max_edge:
                    im.thumbnail((max_edge, max_edge), Image.LANCZOS)
                buf = BytesIO()
                im.save(buf, format="WEBP", quality=quality, method=5)
            abs_dest.parent.mkdir(parents=True, exist_ok=True)
            abs_dest.write_bytes(buf.getvalue())

        asset = MediaAsset.objects.filter(file=rel_dest).first()
        if asset is None:
            asset = MediaAsset(folder=folder, title=title, alt_text=alt,
                               original_filename=Path(src_path).name)
            asset.file.name = rel_dest
            asset.save()
        else:
            changed = False
            if asset.title != title:
                asset.title = title; changed = True
            if asset.alt_text != alt:
                asset.alt_text = alt; changed = True
            if asset.folder_id != folder.id:
                asset.folder = folder; changed = True
            if changed:
                asset.save()
        return asset
