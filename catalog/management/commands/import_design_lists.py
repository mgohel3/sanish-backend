"""
Import the client's per-range "design index" CSVs (S Shade, Cool Colours,
THREE, SANISH 0.8) into the catalogue.

Unlike the older image-folder imports (import_cool_colors, import_sheet_range)
these CSVs list every DESIGN NO + FINISH combination that exists in a range —
one design number commonly has several finish variants (e.g. 6012 exists in
AB, EN, HB, MM, PL, SF, SM and UG finishes), and each combination is its own
product. Per the client:

    product name  = "<DESIGN NO> <FINISH>"   e.g. "6012 AB"
    product sku   = same as the name          "6012 AB"
    product slug  = slugified name             "6012-ab"

No images are attached yet (client will supply them later), so imported
products are left in --status (default: draft) until photos are added.

Existing products in the target collection that were imported the old way
(bare design-number sku, e.g. "15149") are removed and replaced by the new
per-finish products, per the client's instruction — a plain design number is
not a real product once a range has documented finishes.

Idempotent: re-running updates rows already imported in place (matched by sku).

Usage:
    python manage.py import_design_lists --dry-run
    python manage.py import_design_lists
    python manage.py import_design_lists --status published
"""
import csv
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from catalog.models import Category, Collection, Product

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "design_lists"

# file -> (collection slug, range label, thickness override or None to read from CSV)
RANGES = [
    {
        "file": "s_shade.csv",
        "collection_slug": "sshades",
        "range_label": "S'Shades",
    },
    {
        "file": "cool_colors.csv",
        "collection_slug": "cool-colour",
        "range_label": "Cool Colour",
    },
    {
        "file": "three.csv",
        "collection_slug": "thre3",
        "range_label": "Thre3",
    },
    {
        "file": "sanish_0_8.csv",
        "collection_slug": "perspective-v4",
        "range_label": "Perspective V4",
    },
]

CATEGORY_SLUG = "laminates"

# Matches the sku pattern produced by the old bare-design-number imports
# (import_cool_colors / import_sheet_range), e.g. "15149", "6005-5", "6007-2".
# Only products matching this are considered for cleanup — hand-authored seed
# products (e.g. "SL-0010", "ONH-001") are left alone.
BARE_CODE_SKU_RE = re.compile(r"^\d+(-\d+)?$")

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

FEATURES = [
    "Scratch Resistant",
    "Moisture Proof",
    "Anti-Fingerprint",
    "Easy to Clean",
    "Fire Retardant",
]


def normalize_thickness(raw):
    raw = raw.strip().upper().replace("MM", "").strip()
    value = float(raw)
    return f"{value:g}mm"


def parse_csv(path):
    """Yield (thickness, design_no, finish) for each data row; skips the title
    row, header row, blank rows and the trailing TOTAL row."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    for row in rows[2:]:  # row 0 = title, row 1 = column headers
        if not row or not row[0].strip():
            continue
        thickness_raw, design_no, finish = row[0].strip(), row[1].strip(), row[2].strip()
        if thickness_raw.upper() == "TOTAL" or not design_no or not finish:
            continue
        yield normalize_thickness(thickness_raw), design_no, finish.upper()


class Command(BaseCommand):
    help = "Import design-index CSVs (design no + finish per row) into the catalogue."

    def add_arguments(self, parser):
        parser.add_argument("--dir", default=str(FIXTURES_DIR),
                            help="Directory containing the range CSV files")
        parser.add_argument("--status", default="draft", choices=["draft", "published"],
                            help="Status for imported products (default: draft — no images yet)")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        source_dir = Path(opts["dir"])
        status = opts["status"]

        try:
            category = Category.objects.get(slug=CATEGORY_SLUG)
        except Category.DoesNotExist:
            raise CommandError(f"Category '{CATEGORY_SLUG}' does not exist")

        collections = {}
        for r in RANGES:
            try:
                collections[r["collection_slug"]] = Collection.objects.get(slug=r["collection_slug"])
            except Collection.DoesNotExist:
                raise CommandError(f"Collection '{r['collection_slug']}' does not exist")

        plan = []  # (range_config, collection, list of (thickness, design_no, finish))
        for r in RANGES:
            path = source_dir / r["file"]
            if not path.is_file():
                raise CommandError(f"Not found: {path}")
            entries = list(parse_csv(path))
            seen = set()
            deduped = []
            for entry in entries:
                if entry in seen:
                    continue
                seen.add(entry)
                deduped.append(entry)
            plan.append((r, collections[r["collection_slug"]], deduped))
            self.stdout.write(f"{r['file']}: {len(deduped)} unique design+finish rows "
                              f"-> collection '{r['collection_slug']}'")

        if opts["dry_run"]:
            total = sum(len(entries) for _, _, entries in plan)
            self.stdout.write(f"\nDry run — would import {total} products total. "
                              "No changes made.")
            return

        created = updated = removed = 0
        with transaction.atomic():
            for r, collection, entries in plan:
                skus_in_range = []
                for thickness, design_no, finish in entries:
                    name = f"{design_no} {finish}"
                    sku = name
                    skus_in_range.append(sku)

                    product, is_new = Product.objects.get_or_create(
                        sku=sku, defaults={"name": name, "category": category}
                    )
                    product.name              = name
                    product.category          = category
                    product.collection        = collection
                    product.status            = status
                    product.thickness         = thickness
                    product.finish            = finish
                    product.surface           = "Decorative Laminate"
                    product.application       = "Cabinets, Wardrobes, Wall Panels, Shutters, Interiors"
                    product.design_type       = "Solid"
                    product.short_description = SHORT_DESC.format(
                        range=r["range_label"], design_no=design_no,
                        finish=finish, thickness=thickness)
                    product.description       = DESCRIPTION.format(
                        name=name, range=r["range_label"], design_no=design_no,
                        finish=finish, thickness=thickness)
                    product.features          = list(FEATURES)
                    product.tech_specs        = {
                        "Thickness": thickness,
                        "Sheet Size": "2440mm × 1220mm (8ft × 4ft)",
                        "Surface": "Decorative Laminate",
                        "Design No": design_no,
                        "Finish": finish,
                        "Range": r["range_label"],
                    }
                    if not product.accent_color:
                        product.accent_color = "#85addc"
                    if not product.slug:
                        product.slug = slugify(name)
                    product.save()

                    created += is_new
                    updated += (not is_new)

                # Remove old bare-design-number products from this collection that
                # the new per-finish rows replace (per client instruction). Only
                # products matching the old bare-code sku pattern are touched —
                # hand-authored seed products in the same collection are left alone.
                stale_skus = [
                    p.sku for p in Product.objects.filter(collection=collection)
                    .exclude(sku__in=skus_in_range).only("id", "sku")
                    if BARE_CODE_SKU_RE.match(p.sku)
                ]
                n = len(stale_skus)
                if n:
                    Product.objects.filter(sku__in=stale_skus).delete()
                    removed += n
                self.stdout.write(f"  [{collection.slug}] {len(entries)} imported, "
                                  f"{n} stale product(s) removed")

        self.stdout.write(self.style.SUCCESS(
            f"Done — {created} created, {updated} updated, {removed} removed. "
            f"All imported products are status='{status}' (no images yet)."
        ))
