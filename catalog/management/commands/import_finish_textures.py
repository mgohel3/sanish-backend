"""
Import the client's "finish texture" delivery (one folder per range, one photo
per exact shade+finish combination — e.g. "15003-FT.jpg", "6001_TX_UG.jpg",
"3855 (H) RM.jpg") into the Media Library and bind each to its matching
Product by SKU (which is "<code> <finish>", finish sometimes prefixed "H").

Source root (hardcoded per range folder):
    <SOURCE>/COOL COLORS FINISH TEXTURES/<code>-<finish>[(n)].jpg
    <SOURCE>/SANISH 0.8 PERSPECTIVE FINISH TEXTURES/<code>_TX_[(H)]<finish>.jpg
    <SOURCE>/SANISH S'SHADE FINISH TEXTURES/<code>_TX_<finish>.jpg
    <SOURCE>/SANISH THREE FINSH TEXTURES/<code> [(H)] <finish>.jpg

Images are resized (longest edge <= --max-edge, aspect kept) to WebP and
stored under MEDIA_ROOT/products/<collection-slug>/textures/, then a
MediaAsset is created in a "<Range> Textures" Media Library folder (reusing
"Thre3 Textures" for the thre3 range).

For a matched product with no images yet, the texture becomes its main
gallery image (position 0) and the product is published. For a product that
already has an image (e.g. from the earlier shared-code import), the texture
is added as an extra role="texture" image instead, so the accurate
finish-specific swatch doesn't replace the existing shot.

Matching is done on a "degraded" key (code + finish letters, ignoring any
standalone "H" token) because a few filenames omit the "(H)" marker that the
Product SKU carries — this is unambiguous since no product's degraded key
collides with another's in the same collection.

Usage:
    python manage.py import_finish_textures --source "<SOURCE>" --dry-run
    python manage.py import_finish_textures --source "<SOURCE>"
"""
import re
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

from catalog.models import Collection, Product, ProductImage
from media_library.models import MediaAsset, MediaFolder

RANGES = [
    # (source subfolder,                         collection slug,  MediaFolder name)
    ("COOL COLORS FINISH TEXTURES",               "cool-colour",    "Cool Colours Textures"),
    ("SANISH 0.8 PERSPECTIVE FINISH TEXTURES",     "perspective-v4", "Perspective V4 Textures"),
    ("SANISH S'SHADE FINISH TEXTURES",             "sshades",        "S'Shades Textures"),
    ("SANISH THREE FINSH TEXTURES",                "thre3",          "Thre3 Textures"),
]

CODE_RE = re.compile(r"^(\d+)")
LETTERS_RE = re.compile(r"[A-Za-z]+")


def parse_code_finish(stem):
    """'3855 (H) RM' -> ('3855', ['H', 'RM'])  |  '6001_TX_UG' -> ('6001', ['UG'])"""
    m = CODE_RE.match(stem)
    if not m:
        return None
    code = m.group(1)
    rest = stem[m.end():]
    rest = rest.replace("(", " ").replace(")", " ").replace("_", " ").replace("-", " ")
    rest = re.sub(r"(?i)\bTX\b", " ", rest)
    tokens = LETTERS_RE.findall(rest)
    if not tokens:
        return None
    return code, [t.upper() for t in tokens]


def degrade(code, tokens):
    return code + " " + " ".join(t for t in tokens if t != "H")


class Command(BaseCommand):
    help = "Import client finish-texture photos and bind them to matching products by SKU."

    def add_arguments(self, parser):
        parser.add_argument("--source", required=True,
                             help="Path to the TEXTURES folder containing the 4 range subfolders")
        parser.add_argument("--max-edge", type=int, default=2000)
        parser.add_argument("--webp-quality", type=int, default=82)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        source = Path(opts["source"])
        if not source.is_dir():
            raise CommandError(f"Not found: {source}")
        dry = opts["dry_run"]
        max_edge = opts["max_edge"]
        quality = opts["webp_quality"]

        grand_bound = grand_extra = grand_unmatched = grand_published = 0

        for subfolder, coll_slug, folder_name in RANGES:
            src_dir = source / subfolder
            if not src_dir.is_dir():
                self.stdout.write(self.style.WARNING(f"Skip missing folder: {src_dir}"))
                continue
            collection = Collection.objects.filter(slug=coll_slug).first()
            if not collection:
                self.stdout.write(self.style.WARNING(f"Skip {coll_slug}: collection missing"))
                continue

            products = list(Product.objects.filter(collection=collection))
            by_key = {}
            for p in products:
                parsed = parse_code_finish(p.sku)
                if parsed:
                    by_key[degrade(*parsed)] = p

            folder = None
            if not dry:
                folder, _ = MediaFolder.objects.get_or_create(name=folder_name)

            media_subdir = f"products/{coll_slug}/textures"
            files = sorted(f for f in src_dir.iterdir()
                            if f.suffix.lower() in (".jpg", ".jpeg", ".png"))

            bound = extra = unmatched = published = 0
            with transaction.atomic():
                for f in files:
                    parsed = parse_code_finish(f.stem)
                    if not parsed:
                        unmatched += 1
                        continue
                    code, tokens = parsed
                    key = degrade(code, tokens)
                    product = by_key.get(key)
                    if not product:
                        unmatched += 1
                        continue

                    finish_label = " ".join(t for t in tokens if t != "H")
                    dest_name = f"{code}-{'-'.join(tokens)}.webp"
                    rel_dest = f"{media_subdir}/{dest_name}"

                    if dry:
                        bound += 1
                        continue

                    asset = self._asset_for(
                        f, rel_dest, title=f"{code} {finish_label}",
                        alt=f"Sanish {collection.name} shade {code} — {finish_label} finish texture",
                        folder=folder, max_edge=max_edge, quality=quality,
                    )

                    has_image = ProductImage.objects.filter(product=product).exists()
                    if not has_image:
                        ProductImage.objects.create(product=product, asset=asset,
                                                     position=0, role="gallery")
                        if product.status != "published":
                            product.status = "published"
                            product.save(update_fields=["status"])
                            published += 1
                        bound += 1
                    else:
                        next_pos = (ProductImage.objects.filter(product=product)
                                    .order_by("-position").first().position + 1)
                        ProductImage.objects.create(product=product, asset=asset,
                                                     position=next_pos, role="texture",
                                                     label=finish_label)
                        extra += 1

            self.stdout.write(
                f"{coll_slug}: {len(files)} file(s) — {bound} as main image, "
                f"{extra} added as texture swatch, {unmatched} unmatched, "
                f"{published} product(s) newly published")
            grand_bound += bound
            grand_extra += extra
            grand_unmatched += unmatched
            grand_published += published

        verb = "Would process" if dry else "Processed"
        self.stdout.write(self.style.SUCCESS(
            f"{verb} totals — main: {grand_bound}, texture-extra: {grand_extra}, "
            f"unmatched: {grand_unmatched}, newly published: {grand_published}"))

    def _asset_for(self, src_path, rel_dest, *, title, alt, folder, max_edge, quality):
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
        return asset
