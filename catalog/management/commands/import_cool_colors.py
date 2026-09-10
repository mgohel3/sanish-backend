"""
Import the Cool Colours solid-shade laminate range from the client's
"COOL COLORS" delivery folder.

    FULLSHEETS/<code>_ok.jpg   -> main product image (flat sheet swatch)
    PREVIEW/<code>_PW.jpg      -> "applied" preview (shade on furniture in a room)

Every file is named by its numeric shade code (15003, 15013, ...). Per the
client, the product name IS that code. Images are resized so their longest edge
is <= --max-edge px (aspect ratio preserved, never cropped) and stored as WebP
in the Media Library under the "Cool Colours" folder, then attached to the
product as ProductImage rows (position 0 = full sheet, position 1 = preview).

Existing products that are not part of this range are set to draft (not deleted).

Idempotent: re-running updates in place and reuses already-imported media.
"""
import re
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from PIL import Image, ImageOps

from catalog.models import Category, Collection, Product, ProductImage
from media_library.models import MediaAsset, MediaFolder

DEFAULT_SOURCE = (
    r"F:\Client Data\2026\Kalpeshbhai - Karya Graphito\Sanish Website"
    r"\Vivek Sanish Data Received\wetransfer_sanish-data_2026-08-18_1130\COOL COLORS"
)

CATEGORY_SLUG   = "laminates"
COLLECTION_SLUG = "cool-colour"
MEDIA_SUBDIR    = "products/cool-colours"
FOLDER_NAME     = "Cool Colours"

SHORT_DESC = (
    "A cool-toned solid-colour decorative laminate from the Sanish Cool Colours "
    "range (shade {code}) — a clean, contemporary surface that pairs easily with "
    "wood, metal and stone in modern interiors."
)

DESCRIPTION = (
    "<p>{code} is part of the Sanish <strong>Cool Colours</strong> collection — a "
    "curated range of solid-shade decorative laminates built for calm, cohesive "
    "interiors. The surface carries a smooth, even colour from edge to edge, so it "
    "reads cleanly across large runs of shutters, wardrobe fronts and wall "
    "panelling.</p>"
    "<p>Like every Sanish laminate it is scratch resistant, moisture proof and easy "
    "to wipe clean, making it equally at home in kitchens, wardrobes, retail joinery "
    "and commercial fit-outs. Supplied in standard 8ft × 4ft (2440 × 1220 mm) sheets "
    "at 1 mm thickness.</p>"
    "<p>Shade names in this range follow the factory shade code. For exact colour "
    "matching, request a physical sample or download the Cool Colours catalogue from "
    "the catalogue page.</p>"
)

FEATURES = [
    "Scratch Resistant",
    "Moisture Proof",
    "Anti-Fingerprint",
    "Easy to Clean",
    "Fire Retardant",
]

TECH_SPECS = {
    "Thickness": "1.0mm",
    "Sheet Size": "2440mm × 1220mm (8ft × 4ft)",
    "Surface": "Decorative Laminate",
    "Range": "Cool Colours",
}


class Command(BaseCommand):
    help = "Import the Cool Colours laminate range and draft all other products."

    def add_arguments(self, parser):
        parser.add_argument("--source", default=DEFAULT_SOURCE,
                            help="Path to the COOL COLORS folder (contains FULLSHEETS/ and PREVIEW/)")
        parser.add_argument("--max-edge", type=int, default=2000,
                            help="Longest image edge in px after resize (aspect ratio kept)")
        parser.add_argument("--webp-quality", type=int, default=82)
        parser.add_argument("--no-draft-others", action="store_true",
                            help="Leave other products' status untouched")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        source = Path(opts["source"])
        fullsheet_dir = source / "FULLSHEETS"
        preview_dir   = source / "PREVIEW"
        if not fullsheet_dir.is_dir():
            raise CommandError(f"Not found: {fullsheet_dir}")

        try:
            category = Category.objects.get(slug=CATEGORY_SLUG)
        except Category.DoesNotExist:
            raise CommandError(f"Category '{CATEGORY_SLUG}' does not exist")
        try:
            collection = Collection.objects.get(slug=COLLECTION_SLUG)
        except Collection.DoesNotExist:
            raise CommandError(f"Collection '{COLLECTION_SLUG}' does not exist")

        folder, _ = MediaFolder.objects.get_or_create(name=FOLDER_NAME)

        # code -> {"full": Path, "preview": Path|None}
        items = {}
        for f in sorted(fullsheet_dir.iterdir()):
            m = re.match(r"(\d+)", f.name)
            if not m or f.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            items[m.group(1)] = {"full": f, "preview": None}

        if preview_dir.is_dir():
            for f in preview_dir.iterdir():
                m = re.match(r"(\d+)", f.name)
                if m and m.group(1) in items and f.suffix.lower() in (".jpg", ".jpeg", ".png"):
                    # prefer the *_PW.jpg variant if both exist
                    cur = items[m.group(1)]["preview"]
                    if cur is None or "_PW" in f.name.upper():
                        items[m.group(1)]["preview"] = f

        codes = sorted(items)
        self.stdout.write(f"Found {len(codes)} shades "
                          f"({sum(1 for c in codes if items[c]['preview'])} with previews)")
        if opts["dry_run"]:
            for c in codes:
                self.stdout.write(f"  {c}  full={items[c]['full'].name}  "
                                  f"preview={items[c]['preview'].name if items[c]['preview'] else '—'}")
            return

        media_root = Path(settings.MEDIA_ROOT)
        (media_root / MEDIA_SUBDIR).mkdir(parents=True, exist_ok=True)
        max_edge = opts["max_edge"]
        quality  = opts["webp_quality"]

        created = updated = 0
        with transaction.atomic():
            for code in codes:
                full_asset = self._asset_for(
                    items[code]["full"], f"{MEDIA_SUBDIR}/{code}.webp",
                    title=code, alt=f"Sanish Cool Colours laminate — shade {code}",
                    folder=folder, max_edge=max_edge, quality=quality,
                )
                preview_asset = None
                if items[code]["preview"]:
                    preview_asset = self._asset_for(
                        items[code]["preview"], f"{MEDIA_SUBDIR}/{code}-preview.webp",
                        title=f"{code} — applied preview",
                        alt=f"Sanish Cool Colours shade {code} applied to interior joinery",
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
                product.short_description = SHORT_DESC.format(code=code)
                product.description       = DESCRIPTION.format(code=code)
                product.surface          = "Decorative Laminate"
                product.thickness        = "1.0mm"
                product.dimensions       = "8ft × 4ft (2440 × 1220mm)"
                product.application      = "Cabinets, Wardrobes, Wall Panels, Shutters, Interiors"
                product.design_type      = "Solid"
                product.features         = list(FEATURES)
                product.tech_specs       = dict(TECH_SPECS)
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

            if not opts["no_draft_others"]:
                n = Product.objects.exclude(sku__in=codes).exclude(status="draft").update(status="draft")
                self.stdout.write(self.style.WARNING(f"Set {n} other product(s) to draft"))

        self.stdout.write(self.style.SUCCESS(
            f"Done — {created} created, {updated} updated, {len(codes)} Cool Colours published."
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
