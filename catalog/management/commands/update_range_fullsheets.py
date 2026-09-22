"""
Clear and reload ONLY the full-sheet (main/gallery) image for one range, from
its Excel + a Fullsheets folder of "<design>.jpg" photos (one photo per
design, shared by every finish-product of that design). Texture and
application images are never touched — not read, not replaced.

Every product in the current sheet has its EXISTING gallery image cleared
first. Products whose design has a matching file in the folder get the new
one; products whose design has none are left with no gallery image and are
set to draft (their texture/application images are untouched and still show
if you look at the product directly — they're just not the storefront's
"live" set). Re-adding a full sheet later and re-running this command does
not automatically re-publish a drafted product — publish it by hand once the
photo is confirmed, or pass --republish.

Nothing is written without confirmation: run with --dry-run first.

Example:
    python manage.py update_range_fullsheets --range cool-colour \
        --xlsx ".../manish ji cool colour excel sheet data.xlsx" \
        --full ".../Fullsheets" --dry-run
"""
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Collection, Product, ProductImage
from catalog.management.commands.import_range_delivery import (
    RANGES, PROTECTED_FOLDERS, read_products, index_design_dir,
)
from media_library.models import MediaAsset, MediaFolder


class Command(BaseCommand):
    help = "Clear and reload the full-sheet (gallery) image only — texture/application untouched."

    def add_arguments(self, parser):
        parser.add_argument("--range", required=True, choices=sorted(RANGES))
        parser.add_argument("--xlsx", required=True)
        parser.add_argument("--full", required=True, help="Folder of '<design>.jpg' full-sheet photos")
        parser.add_argument("--max-edge", type=int, default=2000)
        parser.add_argument("--webp-quality", type=int, default=82)
        parser.add_argument("--republish", action="store_true",
                            help="Also set back to published any draft product that gets a full sheet in this run.")
        parser.add_argument("--purge-old-media", action="store_true",
                            help="Delete old full-sheet MediaAsset rows/files left referenced by nothing.")
        parser.add_argument("--keep-files", action="store_true",
                            help="With --purge-old-media: delete the rows but leave files on disk.")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        cfg = RANGES[opts["range"]]
        dry = opts["dry_run"]
        w = self.stdout.write
        for key in ("xlsx", "full"):
            if not Path(opts[key]).exists():
                raise CommandError(f"Not found: {opts[key]}")
        try:
            collection = Collection.objects.get(slug=cfg["collection"])
        except Collection.DoesNotExist as exc:
            raise CommandError(str(exc))

        rows = read_products(opts["xlsx"])
        full_idx, strays, dupes = index_design_dir(opts["full"])

        products = []
        for design, finish in rows:
            sku = f"{design} {finish}"
            p = Product.objects.filter(collection=collection, sku=sku).first()
            if p:
                products.append((design, sku, p, full_idx.get(design)))

        have = [x for x in products if x[3]]
        missing = [x for x in products if not x[3]]
        used_designs = {d for d, _, _, f in have}
        was_published_missing = [x for x in missing if x[2].status == "published"]
        was_draft_have = [x for x in have if x[2].status != "published"]

        w(f"\n=== {cfg['label']} full sheets ({'DRY RUN' if dry else 'LIVE'}) — texture/application NOT touched ===")
        w(f"sheet products found in the catalogue: {len(products)} | full-sheet files in folder: {len(full_idx)}")
        w(f"EVERY one of these has its current gallery image cleared first.")
        w(f"  -> {len(have)} get a NEW full sheet (design matched a file)")
        w(f"  -> {len(missing)} get NO full sheet -> set to draft "
          f"({len(was_published_missing)} of those are currently published)")
        if was_draft_have:
            w(f"  {len(was_draft_have)} currently-draft product(s) will receive a full sheet but stay draft "
              f"unless you pass --republish: {[s for _, s, *_ in was_draft_have][:10]}")
        w(f"designs with no matching file: {sorted({d for d, s, p, f in missing})}")
        w(f"full-sheet files not matched to any design in the sheet: {sorted(set(full_idx) - used_designs)}")
        if strays or dupes:
            w(f"odd filenames skipped: {strays} | duplicate design files (larger kept): {dupes}")
        w(f"texture rows untouched: {ProductImage.objects.filter(product__collection=collection, role='texture').count()}")
        w(f"application rows untouched: {ProductImage.objects.filter(product__collection=collection, role='application').count()}")

        if dry:
            self._purge_report(collection, cfg, dry=True, purge=opts["purge_old_media"])
            w(self.style.SUCCESS("Dry run complete — nothing was written."))
            return

        # ── LIVE ─────────────────────────────────────────────────────────
        base = f"products/{collection.slug}"
        folder, _ = MediaFolder.objects.get_or_create(name=cfg["main"])
        q = opts["webp_quality"]
        cache, drafted, replaced, republished = {}, 0, 0, 0

        with transaction.atomic():
            # clear every one of this range's current gallery images up front
            ProductImage.objects.filter(product__collection=collection, product__sku__in=[s for _, s, *_ in products],
                                        role="gallery").delete()

            for design, sku, product, path in have:
                if path.name not in cache:
                    cache[path.name] = self._asset(
                        path, f"{base}/full/{design}.webp", title=design, folder=folder,
                        max_edge=opts["max_edge"], q=q,
                        alt=f"Sanish {cfg['label']} laminate — design {design}")
                ProductImage.objects.create(product=product, asset=cache[path.name], role="gallery", position=0)
                replaced += 1
                if opts["republish"] and product.status != "published":
                    product.status = "published"
                    product.save(update_fields=["status"])
                    republished += 1

            for design, sku, product, _ in missing:
                if product.status != "draft":
                    product.status = "draft"
                    product.save(update_fields=["status"])
                    drafted += 1

        w(self.style.SUCCESS(f"Full sheets replaced on {replaced} product(s). "
                             f"{drafted} product(s) newly set to draft (no full sheet)."
                             + (f" {republished} product(s) republished." if republished else "")))
        w("Texture and application images were not touched.")
        self._purge_report(collection, cfg, dry=False, purge=opts["purge_old_media"], keep_files=opts["keep_files"])

    # ── helpers ──────────────────────────────────────────────────────────
    def _asset(self, src, rel_dest, *, title, alt, folder, max_edge, q):
        from io import BytesIO
        from PIL import Image, ImageOps
        Image.MAX_IMAGE_PIXELS = None
        media_root = Path(settings.MEDIA_ROOT)
        abs_dest = media_root / rel_dest
        with Image.open(src) as im:
            try:
                im.draft("RGB", (max_edge, max_edge))
            except Exception:
                pass
            im = ImageOps.exif_transpose(im).convert("RGB")
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

    def _purge_report(self, collection, cfg, *, dry, purge, keep_files=False):
        w = self.stdout.write
        folder_assets = set(MediaAsset.objects.filter(folder__name=cfg["main"]).values_list("id", flat=True))
        folder_assets -= set(MediaAsset.objects.filter(folder__name__in=PROTECTED_FOLDERS).values_list("id", flat=True))
        still_used = set(ProductImage.objects.values_list("asset_id", flat=True))
        stale = folder_assets - still_used
        size = 0
        for a in MediaAsset.objects.filter(id__in=stale):
            try:
                size += default_storage.size(a.file.name)
            except Exception:
                pass
        w(f"full-sheet assets in '{cfg['main']}' now unreferenced by ANY product: {len(stale)}, ~{size/1e6:.1f} MB"
          f"{'' if purge else '  (left in place — pass --purge-old-media to delete)'}")
        if dry or not purge or not stale:
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
