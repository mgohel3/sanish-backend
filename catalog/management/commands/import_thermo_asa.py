"""
Refresh Thermo ASA product images from the client's CSV index + two flat
image folders. Unlike the laminate ranges (import_range_delivery.py) there
are no finish variants here — one CSV row's "Code Number" is one product,
with at most one full-sheet (gallery) photo and one application photo each.
No texture concept for this range.

CSV columns (as the client provided them):
  Code Number                    — the product's own SKU/name, e.g. "SN 5100"
  Matching laminate               — other code(s) that appear alongside this
                                     one in ITS application photo (informational
                                     only here — see note below)
  Application Image# From Folder  — which "<N>.jpg" in the application folder
                                     is this product's own application shot

Image matching:
  - Full-sheet: "<numeric part of the code>.jpg" in --full, e.g. "SN 5100" ->
    "5100.jpg", "GS 6001" -> "6001.jpg", "9103 STONE" -> "9103.jpg".
  - Application: "<Application Image# From Folder>.jpg" in --application —
    always that row's own number, never anything borrowed from a "Matching
    laminate" partner's row.

A few codes (confirmed by hand: GS 6005, SN 5101, SN 5108) appear on TWO
different rows with two different, genuinely different application photos
(not a duplicate row — the files differ). Since a product page here only
ever shows one application image, the FIRST occurrence in the sheet (by row
order) wins; the dry-run output calls these out explicitly so a human can
override the choice if the other photo is actually the better one.

The "Matching laminate" column is deliberately NOT used to cross-attach a
photo to the partner codes it names (e.g. row 1's photo also depicts "SN
5114 / GS 6002", but SN 5114 and GS 6002 already get their own, more
specific dedicated photos from their own rows) — flagged in the dry-run
report rather than silently applied, since showing multiple application
photos per product isn't something this site's product page currently
supports.

A code with no full-sheet match is left exactly as before: existing image
(if any) untouched, no new gallery image set — only publish based on having
one, otherwise draft. A code with no matching row at all is retired.

Always dry-run first.
"""
import csv
import re
from collections import defaultdict
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from PIL import Image

from catalog.management.commands.import_range_delivery import open_srgb
from catalog.models import Category, Collection, Product, ProductImage
from media_library.models import MediaAsset, MediaFolder

IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp")
COLLECTION_SLUG = "thermo-asa"
CATEGORY_SLUG = "thermo-laminates"
MEDIA_FOLDER = "Thermo ASA"


def norm_code(s):
    s = (s or "").strip().upper()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"^([A-Z]+)(\d)", r"\1 \2", s)  # "SN5108" -> "SN 5108"
    return s


def numeric_part(code):
    m = re.match(r"^([A-Z]+)\s*(\d+)", code)
    if m:
        return m.group(2)
    m2 = re.match(r"^(\d+)", code)
    return m2.group(1) if m2 else None


def read_rows(csv_path):
    """[(code, matching, img_no), ...] in sheet order, codes normalised, blank rows dropped."""
    out = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for r in reader:
            if not r or not (r[0] or "").strip():
                continue
            code = norm_code(r[0])
            matching = norm_code(r[1]) if len(r) > 1 else ""
            img_no = (r[2].strip() if len(r) > 2 else "")
            out.append((code, matching, img_no))
    return out


def index_flat_dir(folder):
    """{stem -> Path} for every image file, keyed by its bare filename stem."""
    files, dupes = {}, []
    for f in sorted(Path(folder).iterdir()):
        if f.suffix.lower() not in IMG_EXTS:
            continue
        stem = f.stem.strip()
        if stem in files:
            dupes.append(f.name)
            if f.stat().st_size > files[stem].stat().st_size:
                files[stem] = f
            continue
        files[stem] = f
    return files, dupes


class Command(BaseCommand):
    help = "Refresh Thermo ASA product images (full-sheet + application) from the client's CSV + folders."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True)
        parser.add_argument("--full", required=True, help="Folder of '<numeric code>.jpg' full-sheet photos")
        parser.add_argument("--application", required=True, help="Folder of '<N>.jpg' application photos")
        parser.add_argument("--max-edge", type=int, default=2000)
        parser.add_argument("--app-max-edge", type=int, default=1600)
        parser.add_argument("--webp-quality", type=int, default=82)
        parser.add_argument("--retire-missing", choices=["draft", "delete", "none"], default="draft",
                            help="Existing products whose code is NOT in the sheet (default: draft)")
        parser.add_argument("--purge-old-media", action="store_true")
        parser.add_argument("--keep-files", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        dry = opts["dry_run"]
        w = self.stdout.write
        for key in ("csv", "full", "application"):
            if not Path(opts[key]).exists():
                raise CommandError(f"Not found: {opts[key]}")

        try:
            category = Category.objects.get(slug=CATEGORY_SLUG)
            collection = Collection.objects.get(slug=COLLECTION_SLUG)
        except (Category.DoesNotExist, Collection.DoesNotExist) as exc:
            raise CommandError(str(exc))

        rows = read_rows(opts["csv"])
        full_idx, full_dupes = index_flat_dir(opts["full"])
        app_idx, app_dupes = index_flat_dir(opts["application"])

        # first-occurrence-wins per code; remember every occurrence for the report
        code_rows = defaultdict(list)
        for code, matching, img_no in rows:
            code_rows[code].append((matching, img_no))
        codes_in_order = list(dict.fromkeys(code for code, _, _ in rows))

        multi = {c: r for c, r in code_rows.items() if len(r) > 1}

        plan = []
        used_full, used_app = set(), set()
        for code in codes_in_order:
            _, img_no = code_rows[code][0]  # first occurrence wins
            num = numeric_part(code)
            full = full_idx.get(num) if num else None
            app = app_idx.get(img_no) if img_no else None
            if full:
                used_full.add(num)
            if app:
                used_app.add(img_no)
            plan.append(dict(code=code, img_no=img_no, full=full, app=app))

        w(f"\n=== Thermo ASA ({'DRY RUN' if dry else 'LIVE'}) ===")
        w(f"sheet: {len(rows)} rows, {len(codes_in_order)} distinct codes | "
          f"files: full={len(full_idx)} application={len(app_idx)}")
        if multi:
            w(f"  codes appearing on more than one row (first occurrence's image wins — "
              f"confirm this is the right photo for each): {len(multi)}")
            for c, occ in multi.items():
                w(f"    {c}: rows give image# {[o[1] for o in occ]} -> using {occ[0][1]}")
        matching_partners = {c: m for c, (m, _) in ((c, code_rows[c][0]) for c in codes_in_order) if m}
        if matching_partners:
            w(f"  'Matching laminate' column present on {len(matching_partners)} row(s) but NOT cross-attached "
              f"to the partner codes (they get their own dedicated photo instead) — say if you want that changed:")
            for c, m in matching_partners.items():
                w(f"    {c} <-> {m}")

        sheet_codes = set(codes_in_order)
        existing = {p.sku: p for p in Product.objects.filter(collection=collection)}
        new_codes = sorted(sheet_codes - set(existing))
        missing = sorted(set(existing) - sheet_codes)
        w(f"products: {len(plan) - len(new_codes)} update-in-place, {len(new_codes)} new, "
          f"{len(missing)} to retire ({opts['retire_missing']})")
        if new_codes:
            w(f"  NEW: {new_codes}")
        if missing:
            pub = [s for s in missing if existing[s].status == "published"]
            w(f"  RETIRE ({len(pub)} currently published): {missing}")

        no_full = sorted({p["code"] for p in plan if not p["full"]})
        no_app = sorted({p["code"] for p in plan if not p["app"]})
        w(f"images: full-sheet matched={sum(1 for p in plan if p['full'])} "
          f"application matched={sum(1 for p in plan if p['app'])}")
        w(f"  codes with NO full-sheet file: {len(no_full)}  {no_full}")
        w(f"  codes with NO application file: {len(no_app)}  {no_app}")
        stray_full = sorted(set(full_idx) - used_full)
        stray_app = sorted(set(app_idx) - used_app, key=lambda x: int(x) if x.isdigit() else 0)
        w(f"  stray full-sheet files (not matched to any code — likely leftover from another delivery): {stray_full}")
        w(f"  stray application files (never referenced by the sheet): {stray_app}")
        if full_dupes or app_dupes:
            w(f"  duplicate filenames on disk (larger kept): full={full_dupes} application={app_dupes}")

        if dry:
            w(self.style.SUCCESS("Dry run complete — nothing was written."))
            return

        # ── LIVE ─────────────────────────────────────────────────────────
        folder, _ = MediaFolder.objects.get_or_create(name=MEDIA_FOLDER)
        base = f"products/{collection.slug}"
        q = opts["webp_quality"]
        cache, created, updated, drafted, published_ct = {}, 0, 0, 0, 0
        old_asset_ids = set()

        with transaction.atomic():
            for i, p in enumerate(plan, 1):
                code = p["code"]
                product = existing.get(code)
                is_new = product is None
                if is_new:
                    product = Product(
                        sku=code, name=code, category=category, collection=collection,
                        surface="Decorative Laminate", design_type="Solid", accent_color="#85addc",
                        features=["Scratch Resistant", "Moisture Proof", "Weather Resistant", "UV Stable"],
                        slug=code.lower().replace(" ", "-"),
                        short_description=f"A weather-resistant Thermo ASA sheet from the Sanish "
                                          f"Thermo ASA range — code {code}.",
                        description=f"<p>{code} is part of the Sanish <strong>Thermo ASA</strong> range "
                                   f"— weather-resistant ASA sheets engineered for outdoor furniture, "
                                   f"cladding and high-exposure architectural applications.</p>",
                    )

                old_gallery = None
                if not is_new:
                    old_gallery = product.product_images.filter(role="gallery").first()

                gallery_asset = None
                if p["full"]:
                    key = f"full:{p['full'].name}"
                    if key not in cache:
                        cache[key] = self._asset(
                            p["full"], f"{base}/full/{numeric_part(code)}.webp",
                            title=code, folder=folder, max_edge=opts["max_edge"], q=q,
                            alt=f"Sanish Thermo ASA sheet — {code}")
                    gallery_asset = cache[key]
                elif old_gallery:
                    gallery_asset = old_gallery.asset  # keep whatever was already there

                app_asset = None
                if p["app"]:
                    key = f"app:{p['app'].name}"
                    if key not in cache:
                        cache[key] = self._asset(
                            p["app"], f"{base}/application/{p['img_no']}.webp",
                            title=f"{code} — application", folder=folder, max_edge=opts["app_max_edge"], q=q,
                            alt=f"Sanish Thermo ASA — {code} applied to exterior cladding")
                    app_asset = cache[key]

                product.status = "published" if gallery_asset else "draft"
                product.save()
                if is_new:
                    created += 1
                else:
                    updated += 1
                if product.status == "published":
                    published_ct += 1

                if not is_new:
                    old_asset_ids |= set(product.product_images.values_list("asset_id", flat=True))
                    product.product_images.all().delete()
                pos = 0
                if gallery_asset:
                    ProductImage.objects.create(product=product, asset=gallery_asset, position=pos, role="gallery")
                    pos += 1
                if app_asset:
                    ProductImage.objects.create(product=product, asset=app_asset, position=pos, role="application")
                    pos += 1

            if missing and opts["retire_missing"] == "draft":
                n = Product.objects.filter(sku__in=missing).exclude(status="draft").update(status="draft")
                w(f"retired to draft: {n} (of {len(missing)} not in sheet)")
            elif missing and opts["retire_missing"] == "delete":
                for s in missing:
                    old_asset_ids |= set(existing[s].product_images.values_list("asset_id", flat=True))
                Product.objects.filter(sku__in=missing).delete()
                w(f"deleted retired products: {len(missing)}")

        w(self.style.SUCCESS(
            f"Products: {created} created, {updated} updated in place, "
            f"{published_ct}/{len(plan)} published."))
        self._purge_report(old_asset_ids, purge=opts["purge_old_media"], keep_files=opts["keep_files"])

    # ── helpers ──────────────────────────────────────────────────────────
    def _asset(self, src, rel_dest, *, title, alt, folder, max_edge, q):
        Image.MAX_IMAGE_PIXELS = None
        media_root = Path(settings.MEDIA_ROOT)
        abs_dest = media_root / rel_dest
        im = open_srgb(src, max_edge=max_edge)
        if max(im.size) > max_edge:
            im.thumbnail((max_edge, max_edge), Image.LANCZOS)
        width, height = im.size
        buf = BytesIO()
        im.save(buf, format="WEBP", quality=q, method=5)
        abs_dest.parent.mkdir(parents=True, exist_ok=True)
        abs_dest.write_bytes(buf.getvalue())
        asset = MediaAsset.objects.filter(file=rel_dest).first()
        if asset is None:
            asset = MediaAsset(folder=folder, title=title, alt_text=alt, original_filename=Path(src).name,
                               width=width, height=height)
            asset.file.name = rel_dest
            asset.webp_version.name = rel_dest
            asset.save()
        else:
            asset.title, asset.alt_text, asset.folder, asset.width, asset.height = title, alt, folder, width, height
            if not asset.webp_version:
                asset.webp_version.name = rel_dest
            asset.save()
        return asset

    def _purge_report(self, old_asset_ids, *, purge, keep_files):
        w = self.stdout.write
        still_used = set(ProductImage.objects.values_list("asset_id", flat=True))
        stale = old_asset_ids - still_used
        size = 0
        for a in MediaAsset.objects.filter(id__in=stale):
            try:
                size += default_storage.size(a.file.name)
            except Exception:
                pass
        w(f"old media that becomes unreferenced: {len(stale)} asset(s), ~{size/1e6:.1f} MB on disk"
          f"{'' if purge else '  (left in place — pass --purge-old-media to delete)'}")
        if not purge or not stale:
            return
        assets = list(MediaAsset.objects.filter(id__in=stale))
        names = set()
        for a in assets:
            names |= ({a.file.name} | ({a.webp_version.name} if a.webp_version else set())) - {""}
        MediaAsset.objects.filter(id__in=stale).delete()
        if keep_files:
            w(self.style.SUCCESS(f"purged {len(assets)} unreferenced asset row(s); files left on disk"))
            return
        removed = 0
        for n in names:
            if MediaAsset.objects.filter(file=n).exists() or MediaAsset.objects.filter(webp_version=n).exists():
                continue
            try:
                default_storage.delete(n)
                removed += 1
            except Exception:
                pass
        w(self.style.SUCCESS(f"purged {len(assets)} asset row(s), {removed} file(s) removed"))
