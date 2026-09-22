"""
Refresh ONLY the texture swatches for one range, from its Excel + Texture
folder. Full-sheet (gallery) and application images are never touched — not
read, not replaced, not even re-encoded — regardless of what they currently
are. Use this instead of import_range_delivery when only new texture photos
have arrived.

Matching (design -> Excel rows -> texture files) reuses the exact same logic
as import_range_delivery, imported from that module so the two commands can
never silently disagree on how a filename maps to a product.

With --sibling-textures (recommended — this is now the standing rule for
Cool Colour) every product of a design gets ALL of that design's matched
finish textures as swatches, fixed alphabetical order, not just its own.
Without it, a product gets only its own finish's texture.

A product whose design has no matching texture file in this run keeps
whatever texture swatches it already had (nothing is cleared for it).

Nothing is written without confirmation: run with --dry-run first.

Example:
    python manage.py update_range_textures --range cool-colour \
        --xlsx ".../manish ji cool colour excel sheet data.xlsx" \
        --texture ".../Texture" --sibling-textures --dry-run
"""
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Collection, Product, ProductImage
from catalog.management.commands.import_range_delivery import (
    RANGES, PROTECTED_FOLDERS, finish_tokens, read_products, index_texture_dir, degrade,
)
from media_library.models import MediaAsset, MediaFolder


class Command(BaseCommand):
    help = "Refresh texture swatches for one range only — full-sheet/application images are never touched."

    def add_arguments(self, parser):
        parser.add_argument("--range", required=True, choices=sorted(RANGES))
        parser.add_argument("--xlsx", required=True)
        parser.add_argument("--texture", required=True, help="Folder of '<design> <FINISH>.jpg' texture photos")
        parser.add_argument("--tex-max-edge", type=int, default=1200)
        parser.add_argument("--webp-quality", type=int, default=82)
        parser.add_argument("--sibling-textures", action="store_true",
                            help="Show every finish of a design on each of its products, not just its own.")
        parser.add_argument("--purge-old-media", action="store_true",
                            help="Delete texture MediaAsset rows/files from this range's Textures folder "
                                 "that end up referenced by nothing after this run.")
        parser.add_argument("--keep-files", action="store_true",
                            help="With --purge-old-media: delete the rows but leave files on disk.")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        cfg = RANGES[opts["range"]]
        dry = opts["dry_run"]
        w = self.stdout.write
        for key in ("xlsx", "texture"):
            if not Path(opts[key]).exists():
                raise CommandError(f"Not found: {opts[key]}")
        try:
            collection = Collection.objects.get(slug=cfg["collection"])
        except Collection.DoesNotExist as exc:
            raise CommandError(str(exc))

        rows = read_products(opts["xlsx"])
        tex_exact, tex_degraded, tex_bad = index_texture_dir(opts["texture"])

        plan = []       # (design, finish, tokens, sku, tex_path|None)
        used = set()
        for design, finish in rows:
            tokens = finish_tokens(finish)
            tex = tex_exact.get((design, tuple(tokens)))
            if tex is None:
                cands = tex_degraded.get(degrade(design, tokens), [])
                if len(cands) == 1:
                    tex = cands[0]
            if tex is not None:
                used.add(tex.name)
            plan.append((design, finish, tokens, f"{design} {finish}", tex))

        matched = [p for p in plan if p[4]]
        unmatched_products = [p for p in plan if not p[4]]
        all_tex_files = {f.name for v in tex_degraded.values() for f in v}
        stray = sorted(all_tex_files - used)

        w(f"\n=== {cfg['label']} textures ({'DRY RUN' if dry else 'LIVE'}) — full-sheet/application NOT touched ===")
        w(f"sheet: {len(plan)} products | texture files in folder: {sum(len(v) for v in tex_degraded.values())}")
        w(f"products getting a new texture this run: {len(matched)}")
        w(f"products with NO matching texture file (their existing swatches, if any, are left as-is): "
          f"{len(unmatched_products)}  {[p[3] for p in unmatched_products][:12]}{' …' if len(unmatched_products) > 12 else ''}")
        w(f"texture files not matched to any product: {len(stray)}  {stray[:10]}")
        if tex_bad:
            w(f"unparseable filenames (skipped): {tex_bad}")

        if opts["sibling_textures"]:
            by_design = {}
            for design, finish, tokens, sku, tex in matched:
                by_design.setdefault(design, []).append((finish, tokens, tex))
            n_rows = sum(len(v) * sum(1 for d2, f2, t2, s2, tx2 in plan if d2 == d) for d in {d for d, *_ in matched}
                        for v in [by_design[d]])
        w(f"products whose MAIN image (gallery) will change: 0 (never touched)")
        w(f"products whose application image will change: 0 (never touched)")

        if dry:
            self._purge_report(collection, cfg, matched, dry=True, purge=opts["purge_old_media"])
            w(self.style.SUCCESS("Dry run complete — nothing was written."))
            return

        # ── LIVE ─────────────────────────────────────────────────────────
        base = f"products/{collection.slug}"
        folder, _ = MediaFolder.objects.get_or_create(name=cfg["tex"])
        q = opts["webp_quality"]
        cache = {}
        updated = 0

        with transaction.atomic():
            for design, finish, tokens, sku, tex in matched:
                lbl = " ".join(t for t in tokens if t != "H")
                if tex.name not in cache:
                    cache[tex.name] = self._asset(
                        tex, f"{base}/texture/{design}-{'-'.join(tokens)}.webp",
                        title=f"{design} {lbl}", folder=folder, max_edge=opts["tex_max_edge"], q=q,
                        alt=f"Sanish {cfg['label']} design {design} — {lbl} finish texture")

            for design, finish, tokens, sku, _tex in plan:
                product = Product.objects.filter(collection=collection, sku=sku).first()
                if not product:
                    continue
                if opts["sibling_textures"]:
                    siblings = sorted(
                        ((f2, tokens2, tex2) for d2, f2, tokens2, s2, tex2 in matched if d2 == design),
                        key=lambda x: " ".join(t for t in x[1] if t != "H"))
                else:
                    own = next((m for m in matched if m[3] == sku), None)
                    siblings = [(own[1], own[2], own[4])] if own else []
                if not siblings:
                    continue        # nothing new for this design — leave the product's textures as they are
                product.product_images.filter(role="texture").delete()
                for i, (f2, tokens2, tex2) in enumerate(siblings):
                    lbl2 = " ".join(t for t in tokens2 if t != "H")
                    ProductImage.objects.create(product=product, asset=cache[tex2.name],
                                                role="texture", label=lbl2, position=100 + i)
                updated += 1

        w(self.style.SUCCESS(f"Updated texture swatches on {updated} product(s). "
                             f"Full-sheet and application images were not touched."))
        self._purge_report(collection, cfg, matched, dry=False, purge=opts["purge_old_media"],
                           keep_files=opts["keep_files"])

    # ── helpers ──────────────────────────────────────────────────────────
    def _asset(self, src, rel_dest, *, title, alt, folder, max_edge, q):
        from io import BytesIO
        from PIL import Image, ImageOps
        Image.MAX_IMAGE_PIXELS = None
        media_root = Path(settings.MEDIA_ROOT)
        abs_dest = media_root / rel_dest
        width = height = None
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
            asset.title, asset.alt_text, asset.folder = title, alt, folder
            asset.width, asset.height = width, height
            if not asset.webp_version:
                asset.webp_version.name = rel_dest
            asset.save()
        return asset

    def _purge_report(self, collection, cfg, matched, *, dry, purge, keep_files=False):
        w = self.stdout.write
        folder_assets = set(MediaAsset.objects.filter(folder__name=cfg["tex"]).values_list("id", flat=True))
        folder_assets -= set(MediaAsset.objects.filter(folder__name__in=PROTECTED_FOLDERS).values_list("id", flat=True))
        still_used = set(ProductImage.objects.values_list("asset_id", flat=True))
        stale = folder_assets - still_used
        size = 0
        for a in MediaAsset.objects.filter(id__in=stale):
            try:
                size += default_storage.size(a.file.name)
            except Exception:
                pass
        w(f"texture assets in '{cfg['tex']}' now unreferenced by ANY product: {len(stale)}, ~{size/1e6:.1f} MB"
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
