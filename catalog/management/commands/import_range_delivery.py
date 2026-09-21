"""
Refresh ONE range (S'Shades / Thre3 / Cool Colour) from the client's
"data received" delivery: a per-range Excel + three image folders.

    <xlsx>            Design Number x Finish rows  -> the product list
    --full   <dir>    <design>.jpg               -> main gallery image (per design)
    --application <dir> <design>.jpg             -> "applied in a room" shot (per design)
    --texture <dir>   <design> <FINISH>.jpg      -> finish texture (per product)

The Excel has two side-by-side lists that are NOT row-aligned (the product list
and an inventory of delivered files), so images are joined to products by
FILENAME, never by row. Only columns 1-2 (design, finish) are read.

Product identity is the SKU "<design> <finish>" with "(H)" written as "H"
(the sheet says "3855 (H) RM", the catalogue has "3855 H RM"). Existing
products are updated IN PLACE (ids / slugs / URLs stay stable); products in the
sheet that don't exist yet are created; products in the range that are no
longer in the sheet are retired (default: set to draft, reversible).

Images for every product that receives at least one new image are replaced; a
product that received nothing keeps whatever it had (and is reported).

Images are resized (aspect kept, never cropped) and written as WebP under
MEDIA_ROOT/products/<collection>/{full,application,texture}/.  The WebP file
is used directly as both `file` and `webp_version`, so nothing is stored twice.

With --sibling-textures every product of a design lists ALL of that design's finish
textures (alphabetical) in its "Available Textures" swatches, reusing the same files.

Nothing is written without confirmation: run with --dry-run first.

Example:
    python manage.py import_range_delivery --range sshades \
        --xlsx ".../s'shades data upload excel.xlsx" \
        --full ".../Full sheets" --application ".../Application" \
        --texture ".../Texture" --delete-demos --dry-run
"""
import re
import shutil
from collections import Counter, defaultdict
from io import BytesIO
from pathlib import Path

import openpyxl
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from PIL import Image, ImageOps

# Client scans can be enormous (some > 400 megapixels). Trusted local files.
Image.MAX_IMAGE_PIXELS = None

from catalog.models import Category, Collection, Product, ProductImage
from media_library.models import MediaAsset, MediaFolder

RANGES = {
    "sshades": dict(label="S'Shades", collection="sshades",
                    main="S'Shades", tex="S'Shades Textures", app="S'Shades Application"),
    "thre3": dict(label="Thre3", collection="thre3",
                  main="Thre3", tex="Thre3 Textures", app="Thre3 Application"),
    "cool-colour": dict(label="Cool Colour", collection="cool-colour",
                        main="Cool Colours", tex="Cool Colours Textures", app="Cool Colours Application"),
}

# Media Library folders that must never be purged, whatever the range.
PROTECTED_FOLDERS = {"Frontend", "Blog Heroes", "Catalogues PDF", "Thre3 Gallery"}

DESIGN_STEM_RE = re.compile(r"^\d+(?:-\d+)?$")
CODE_RE = re.compile(r"^(\d+)")
LETTERS_RE = re.compile(r"[A-Za-z]+")
IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp")

SHORT_DESC = (
    "A decorative laminate from the Sanish {range} range — design {design_no} "
    "in the {finish} finish, at {thickness} thickness."
)
DESCRIPTION = (
    "<p>{name} is part of the Sanish <strong>{range}</strong> collection — design "
    "{design_no} in the {finish} finish. Supplied in standard 8ft × 4ft "
    "(2440 × 1220 mm) sheets at {thickness} thickness.</p>"
    "<p>Like every Sanish laminate it is scratch resistant, moisture proof and easy "
    "to wipe clean, suited to kitchens, wardrobes, retail joinery and commercial "
    "fit-outs.</p>"
    "<p>For exact colour and texture matching, request a physical sample or "
    "download the {range} catalogue from the catalogue page.</p>"
)
FEATURES = ["Scratch Resistant", "Moisture Proof", "Anti-Fingerprint",
            "Easy to Clean", "Fire Retardant"]


# ── parsing helpers ─────────────────────────────────────────────────────────

def clean_cell(v):
    s = "" if v is None else str(v).strip()
    if re.fullmatch(r"\d+\.0", s):
        s = s[:-2]
    return re.sub(r"\s+", " ", s)


def finish_tokens(finish):
    """'(H) RM' -> ['H', 'RM']"""
    return [t.upper() for t in LETTERS_RE.findall(finish.replace("(", " ").replace(")", " "))]


def canonical_finish(finish):
    return " ".join(finish_tokens(finish))


def parse_texture_stem(stem):
    """'3855 (H) RM' -> ('3855', ['H','RM']) | '10823sc' -> ('10823', ['SC'])
    | '6001_TX_UG' -> ('6001', ['UG'])"""
    m = CODE_RE.match(stem.strip())
    if not m:
        return None
    rest = stem[m.end():]
    rest = rest.replace("(", " ").replace(")", " ").replace("_", " ").replace("-", " ")
    rest = re.sub(r"(?i)\bTX\b", " ", rest)
    tokens = [t.upper() for t in LETTERS_RE.findall(rest)]
    if not tokens:
        return None
    return m.group(1), tokens


def degrade(code, tokens):
    return code + " " + " ".join(t for t in tokens if t != "H")


def read_products(xlsx_path):
    """Yield (design, canonical_finish) rows in sheet order (deduped)."""
    ws = openpyxl.load_workbook(xlsx_path, data_only=True).worksheets[0]
    seen, out = set(), []
    for row in ws.iter_rows(min_row=2, values_only=True):
        design = clean_cell(row[0]) if len(row) > 0 else ""
        finish = canonical_finish(clean_cell(row[1])) if len(row) > 1 else ""
        if not design or not finish:
            continue
        key = (design, finish)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def index_design_dir(folder):
    """{design -> Path} for '<design>.jpg' files; also returns strays."""
    files, strays, dupes = {}, [], []
    for f in sorted(Path(folder).iterdir()):
        if f.suffix.lower() not in IMG_EXTS:
            continue
        stem = f.stem.strip()
        if not DESIGN_STEM_RE.match(stem):
            strays.append(f.name)
            continue
        if stem in files:
            dupes.append(f.name)
            # keep the bigger file
            if f.stat().st_size > files[stem].stat().st_size:
                files[stem] = f
            continue
        files[stem] = f
    return files, strays, dupes


def index_texture_dir(folder):
    exact, degraded, bad = {}, defaultdict(list), []
    for f in sorted(Path(folder).iterdir()):
        if f.suffix.lower() not in IMG_EXTS:
            continue
        parsed = parse_texture_stem(f.stem)
        if not parsed:
            bad.append(f.name)
            continue
        code, tokens = parsed
        exact.setdefault((code, tuple(tokens)), f)
        degraded[degrade(code, tokens)].append(f)
    return exact, degraded, bad


class Command(BaseCommand):
    help = "Refresh one range from the client's Excel + full/application/texture folders."

    def add_arguments(self, parser):
        parser.add_argument("--range", required=True, choices=sorted(RANGES))
        parser.add_argument("--xlsx", required=True)
        parser.add_argument("--full", required=True, help="Folder of <design>.jpg full-sheet images")
        parser.add_argument("--application", required=True, help="Folder of <design>.jpg application images")
        parser.add_argument("--texture", required=True, help="Folder of '<design> <FINISH>.jpg' textures")
        parser.add_argument("--max-edge", type=int, default=2000, help="Full-sheet longest edge (px)")
        parser.add_argument("--app-max-edge", type=int, default=1600)
        parser.add_argument("--tex-max-edge", type=int, default=1200)
        parser.add_argument("--webp-quality", type=int, default=82)
        parser.add_argument("--retire-missing", choices=["draft", "delete", "none"], default="draft",
                            help="Products in the collection but NOT in the sheet (default: draft)")
        parser.add_argument("--delete-demos", action="store_true",
                            help="Delete demo products (sku SL-0000) in this collection")
        parser.add_argument("--delete-skus", default="",
                            help="Comma-separated extra SKUs to delete (e.g. junk test products)")
        parser.add_argument("--purge-old-media", action="store_true",
                            help="Also delete old, now-unreferenced MediaAsset rows AND their files. "
                                 "Without it, old rows/files are left in place.")
        parser.add_argument("--keep-files", action="store_true",
                            help="With --purge-old-media: delete the old MediaAsset ROWS but leave "
                                 "every file on disk untouched.")
        parser.add_argument("--sibling-textures", action="store_true",
                            help="Show EVERY finish of a design as a texture swatch on each of its "
                                 "products (fixed alphabetical order), not just the product's own finish.")
        parser.add_argument("--reuse-existing", action="store_true",
                            help="Skip re-writing image files that already exist at the destination.")
        parser.add_argument("--dry-run", action="store_true")

    # ─────────────────────────────────────────────────────────────────────
    def handle(self, *args, **opts):
        cfg = RANGES[opts["range"]]
        dry = opts["dry_run"]
        self._reuse_existing = opts["reuse_existing"]
        self._ref_errors = []
        for key in ("xlsx", "full", "application", "texture"):
            if not Path(opts[key]).exists():
                raise CommandError(f"Not found: {opts[key]}")

        try:
            category = Category.objects.get(slug="laminates")
            collection = Collection.objects.get(slug=cfg["collection"])
        except (Category.DoesNotExist, Collection.DoesNotExist) as exc:
            raise CommandError(str(exc))

        rows = read_products(opts["xlsx"])
        full_idx, full_strays, full_dupes = index_design_dir(opts["full"])
        app_idx, app_strays, app_dupes = index_design_dir(opts["application"])
        tex_exact, tex_degraded, tex_bad = index_texture_dir(opts["texture"])

        w = self.stdout.write
        w(f"\n=== {cfg['label']} ({'DRY RUN' if dry else 'LIVE'}) ===")
        w(f"sheet: {len(rows)} products, {len({d for d, _ in rows})} designs | "
          f"files: full={len(full_idx)} application={len(app_idx)} texture={sum(len(v) for v in tex_degraded.values())}")

        # ── plan every product ────────────────────────────────────────────
        plan = []
        used_tex, used_full, used_app = set(), set(), set()
        for design, finish in rows:
            tokens = finish_tokens(finish)
            sku = f"{design} {finish}"
            tex = tex_exact.get((design, tuple(tokens)))
            if tex is None:
                cands = tex_degraded.get(degrade(design, tokens), [])
                if len(cands) == 1:
                    tex = cands[0]
            if tex is not None:
                used_tex.add(tex.name)
            full = full_idx.get(design)
            app = app_idx.get(design)
            if full:
                used_full.add(design)
            if app:
                used_app.add(design)
            plan.append(dict(design=design, finish=finish, tokens=tokens, sku=sku,
                             tex=tex, full=full, app=app))

        sheet_skus = {p["sku"] for p in plan}
        existing = {p.sku: p for p in Product.objects.filter(collection=collection)}
        new_skus = sorted(sheet_skus - set(existing))
        missing = sorted(set(existing) - sheet_skus)
        demo_re = re.compile(r"^SL-\d{4}$")
        demos = [s for s in missing if opts["delete_demos"] and demo_re.match(s)]
        extra_del = [s.strip() for s in opts["delete_skus"].split(",") if s.strip()]
        retire = [s for s in missing if s not in demos]

        no_image = [p for p in plan if not (p["full"] or p["tex"] or p["app"])]
        w(f"products: {len(plan) - len(new_skus)} update-in-place, {len(new_skus)} new, "
          f"{len(retire)} to retire ({opts['retire_missing']}), {len(demos)} demo delete, "
          f"{len(extra_del)} extra delete")
        if new_skus:
            w(f"  NEW: {new_skus}")
        if retire:
            pub = [s for s in retire if existing[s].status == "published"]
            w(f"  RETIRE ({len(pub)} currently published): {retire}")
        if demos or extra_del:
            w(f"  DELETE: {demos + extra_del}")
        w(f"images per product: full-sheet={sum(1 for p in plan if p['full'])} "
          f"application={sum(1 for p in plan if p['app'])} texture={sum(1 for p in plan if p['tex'])} "
          f"| no image at all={len(no_image)}")
        if opts["sibling_textures"]:
            by_d = Counter(p["design"] for p in plan if p["tex"])
            w(f"  sibling textures: each product shows all finishes of its design -> "
              f"{sum(n * n for n in by_d.values())} swatch rows (vs {sum(by_d.values())} own-finish only); "
              f"{sum(n for n in by_d.values() if n > 1)} products in {sum(1 for n in by_d.values() if n > 1)} "
              f"multi-finish designs change")
        w(f"  main image will fall back to the texture for "
          f"{sum(1 for p in plan if not p['full'] and p['tex'])} product(s) (no full sheet)")
        d_no_full = sorted({p['design'] for p in plan if not p['full']})
        d_no_app = sorted({p['design'] for p in plan if not p['app']})
        w(f"  designs with NO full sheet: {len(d_no_full)}  {d_no_full[:14]}{' …' if len(d_no_full) > 14 else ''}")
        w(f"  designs with NO application image: {len(d_no_app)}  {d_no_app[:14]}{' …' if len(d_no_app) > 14 else ''}")
        sheet_designs = {p['design'] for p in plan}
        w(f"  stray full-sheet files (design not in sheet): {sorted(set(full_idx) - sheet_designs)} + odd names {full_strays}")
        w(f"  stray application files (design not in sheet): {sorted(set(app_idx) - sheet_designs)} + odd names {app_strays}")
        all_tex_files = {f.name for v in tex_degraded.values() for f in v}
        w(f"  stray texture files (not matched to any product): {sorted(all_tex_files - used_tex)} + unparseable {tex_bad}")
        if full_dupes or app_dupes:
            w(f"  duplicate design files: full={full_dupes} application={app_dupes} (larger kept)")

        if dry:
            self._report_purge(plan, existing, retire, demos, extra_del, cfg, opts, dry_only=True)
            w(self.style.SUCCESS("Dry run complete — nothing was written."))
            return

        # ── LIVE ─────────────────────────────────────────────────────────
        media_root = Path(settings.MEDIA_ROOT)
        base = f"products/{collection.slug}"
        f_main, _ = MediaFolder.objects.get_or_create(name=cfg["main"])
        f_tex, _ = MediaFolder.objects.get_or_create(name=cfg["tex"])
        f_app, _ = MediaFolder.objects.get_or_create(name=cfg["app"])
        q = opts["webp_quality"]
        thickness = self._range_thickness(collection)

        old_asset_ids = set()
        created = updated = kept_existing = 0
        asset_cache = {}

        with transaction.atomic():
            for i, p in enumerate(plan, 1):
                design, finish, sku = p["design"], p["finish"], p["sku"]
                label_finish = " ".join(t for t in p["tokens"] if t != "H")
                product = existing.get(sku)
                is_new = product is None
                if is_new:
                    product = Product(sku=sku, name=sku, category=category, collection=collection,
                                      thickness=thickness, finish=finish, surface="Decorative Laminate",
                                      application="Cabinets, Wardrobes, Wall Panels, Shutters, Interiors",
                                      design_type="Solid", accent_color="#85addc",
                                      features=list(FEATURES), slug=slugify(sku),
                                      short_description=SHORT_DESC.format(range=cfg["label"], design_no=design,
                                                                          finish=finish, thickness=thickness),
                                      description=DESCRIPTION.format(name=sku, range=cfg["label"], design_no=design,
                                                                     finish=finish, thickness=thickness),
                                      tech_specs={"Thickness": thickness, "Sheet Size": "2440mm × 1220mm (8ft × 4ft)",
                                                  "Surface": "Decorative Laminate", "Design No": design,
                                                  "Finish": finish, "Range": cfg["label"]})

                have_new = bool(p["full"] or p["tex"] or p["app"])
                if not have_new:
                    if is_new:
                        product.status = "draft"
                        product.save()
                        created += 1
                    else:
                        kept_existing += 1
                    continue

                gallery_asset = None
                if p["full"]:
                    gallery_asset = self._asset(asset_cache, p["full"], f"{base}/full/{design}.webp",
                                                title=design, folder=f_main, max_edge=opts["max_edge"], q=q,
                                                alt=f"Sanish {cfg['label']} laminate — design {design}")
                elif p["tex"]:
                    gallery_asset = self._asset(asset_cache, p["tex"], f"{base}/texture/{design}-{'-'.join(p['tokens'])}.webp",
                                                title=f"{design} {label_finish}", folder=f_tex,
                                                max_edge=opts["tex_max_edge"], q=q,
                                                alt=f"Sanish {cfg['label']} design {design} — {label_finish} finish")
                app_asset = None
                if p["app"]:
                    app_asset = self._asset(asset_cache, p["app"], f"{base}/application/{design}.webp",
                                            title=f"{design} — application", folder=f_app,
                                            max_edge=opts["app_max_edge"], q=q,
                                            alt=f"Sanish {cfg['label']} design {design} applied to interior joinery")
                tex_assets = []            # [(finish label, MediaAsset)] in display order
                tex_source = ([sp for sp in plan if sp["design"] == design and sp["tex"]]
                              if opts["sibling_textures"] else ([p] if p["tex"] else []))
                for sp in sorted(tex_source, key=lambda sp: " ".join(t for t in sp["tokens"] if t != "H")):
                    lbl = " ".join(t for t in sp["tokens"] if t != "H")
                    tex_assets.append((lbl, self._asset(
                        asset_cache, sp["tex"], f"{base}/texture/{sp['design']}-{'-'.join(sp['tokens'])}.webp",
                        title=f"{sp['design']} {lbl}", folder=f_tex,
                        max_edge=opts["tex_max_edge"], q=q,
                        alt=f"Sanish {cfg['label']} design {sp['design']} — {lbl} finish texture")))

                product.status = "published"
                product.save()
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
                for lbl, tex_asset in tex_assets:
                    ProductImage.objects.create(product=product, asset=tex_asset, position=pos,
                                                role="texture", label=lbl)
                    pos += 1
                created += is_new
                updated += (not is_new)
                if i % 25 == 0:
                    w(f"  … {i}/{len(plan)}")

            # ── retire / delete ──────────────────────────────────────────
            if retire and opts["retire_missing"] == "draft":
                n = Product.objects.filter(sku__in=retire).exclude(status="draft").update(status="draft")
                w(f"retired to draft: {n} (of {len(retire)} not in sheet)")
            elif retire and opts["retire_missing"] == "delete":
                for s in retire:
                    old_asset_ids |= set(existing[s].product_images.values_list("asset_id", flat=True))
                n, _ = Product.objects.filter(sku__in=retire).delete()
                w(f"deleted retired products: {len(retire)}")
            del_list = demos + extra_del
            if del_list:
                for prod in Product.objects.filter(sku__in=del_list):
                    old_asset_ids |= set(prod.product_images.values_list("asset_id", flat=True))
                Product.objects.filter(sku__in=del_list).delete()
                w(f"deleted demo/junk products: {del_list}")

        w(self.style.SUCCESS(f"Products: {created} created, {updated} updated in place, "
                             f"{kept_existing} kept their existing images (nothing new delivered)."))
        self._report_purge(plan, existing, retire, demos, extra_del, cfg, opts, dry_only=False,
                           old_asset_ids=old_asset_ids)

    # ── helpers ───────────────────────────────────────────────────────────
    def _range_thickness(self, collection):
        vals = [t for t in Product.objects.filter(collection=collection).exclude(thickness="")
                .values_list("thickness", flat=True)]
        return Counter(vals).most_common(1)[0][0] if vals else "1.0mm"

    def _asset(self, cache, src, rel_dest, *, title, alt, folder, max_edge, q):
        if rel_dest in cache:
            return cache[rel_dest]
        media_root = Path(settings.MEDIA_ROOT)
        abs_dest = media_root / rel_dest
        width = height = None
        if self._reuse_existing and abs_dest.exists():
            pass
        else:
            src_path = Path(src)
            copied = False
            if src_path.suffix.lower() == ".webp":
                # Already a resized WebP (e.g. produced by an earlier run): copy it as-is
                # instead of re-encoding, so quality is not degraded a second time.
                with Image.open(src_path) as im:
                    w0, h0 = im.size
                if max(w0, h0) <= max_edge:
                    abs_dest.parent.mkdir(parents=True, exist_ok=True)
                    if src_path.resolve() != abs_dest.resolve():
                        shutil.copyfile(src_path, abs_dest)
                    width, height = w0, h0
                    copied = True
            if not copied:
                with Image.open(src_path) as im:
                    try:                   # JPEG DCT down-scaling: huge speed-up on giant scans
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
            asset = MediaAsset(folder=folder, title=title, alt_text=alt, original_filename=Path(src).name)
            asset.file.name = rel_dest
            asset.webp_version.name = rel_dest       # serve the resized WebP itself; no second copy
            if width and height:
                asset.width, asset.height = width, height
            asset.save()
        else:
            changed = False
            for attr, val in (("title", title), ("alt_text", alt)):
                if getattr(asset, attr) != val:
                    setattr(asset, attr, val)
                    changed = True
            if asset.folder_id != folder.id:
                asset.folder = folder
                changed = True
            if not asset.webp_version:
                asset.webp_version.name = rel_dest
                changed = True
            if changed:
                asset.save()
        cache[rel_dest] = asset
        return asset

    def _other_refs(self, ids):
        """Asset ids (from `ids`) still referenced by anything except ProductImage.
        Any relation that cannot be checked is recorded in self._ref_errors."""
        ids = set(ids)
        used = set()
        for rel in MediaAsset._meta.related_objects:
            model = rel.related_model
            if model is ProductImage:
                continue
            if rel.many_to_many and getattr(rel, "through", None) is ProductImage:
                continue
            name = rel.field.name
            try:
                used |= set(model.objects.filter(**{f"{name}__in": ids})
                            .values_list(name, flat=True)) & ids
            except Exception as exc:
                self._ref_errors.append(f"{model._meta.label}.{name}: {exc}")
        return used

    def _report_purge(self, plan, existing, retire, demos, extra_del, cfg, opts, *, dry_only, old_asset_ids=None):
        """Work out (and, with --purge-old-media, perform) removal of old, unreferenced media."""
        w = self.stdout.write
        folders = {cfg["main"], cfg["tex"], cfg["app"]}
        touched_skus = {p["sku"] for p in plan if (p["full"] or p["tex"] or p["app"])}
        if old_asset_ids is None:      # dry run: assets that would be replaced
            old_asset_ids = set()
            for s in touched_skus & set(existing):
                old_asset_ids |= set(existing[s].product_images.values_list("asset_id", flat=True))
            if opts["retire_missing"] == "delete":
                for s in retire:
                    old_asset_ids |= set(existing[s].product_images.values_list("asset_id", flat=True))
            for s in demos + extra_del:
                prod = Product.objects.filter(sku=s).first()
                if prod:
                    old_asset_ids |= set(prod.product_images.values_list("asset_id", flat=True))
        folder_ids = set(MediaAsset.objects.filter(folder__name__in=folders).values_list("id", flat=True))
        cand = old_asset_ids | folder_ids
        cand -= set(MediaAsset.objects.filter(folder__name__in=PROTECTED_FOLDERS).values_list("id", flat=True))
        if dry_only:
            # products that will lose their images -> exclude what other (untouched) products still use
            still = set(ProductImage.objects.exclude(
                product__sku__in=(touched_skus | set(demos) | set(extra_del) |
                                  (set(retire) if opts["retire_missing"] == "delete" else set()))
            ).values_list("asset_id", flat=True))
        else:
            still = set(ProductImage.objects.values_list("asset_id", flat=True))
        cand = cand - still - self._other_refs(cand)
        if self._ref_errors:
            w(self.style.ERROR("could not verify references, NOT purging: " + "; ".join(self._ref_errors)))
            return
        size = 0
        for a in MediaAsset.objects.filter(id__in=cand).only("file", "webp_version"):
            for f in {a.file.name, a.webp_version.name if a.webp_version else ""} - {""}:
                try:
                    size += default_storage.size(f)
                except Exception:
                    pass
        w(f"old media that becomes unreferenced: {len(cand)} asset(s), ~{size / 1e6:.0f} MB on disk"
          f"{'' if opts['purge_old_media'] else '  (left in place — pass --purge-old-media to delete)'}")
        if dry_only or not opts["purge_old_media"]:
            return
        # delete rows, then files no remaining row points at
        assets = list(MediaAsset.objects.filter(id__in=cand))
        names = set()
        for a in assets:
            names |= ({a.file.name} | ({a.webp_version.name} if a.webp_version else set())) - {""}
        MediaAsset.objects.filter(id__in=cand).delete()
        if opts["keep_files"]:
            w(self.style.SUCCESS(f"purged {len(assets)} asset row(s); {len(names)} file(s) left on disk (--keep-files)"))
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
