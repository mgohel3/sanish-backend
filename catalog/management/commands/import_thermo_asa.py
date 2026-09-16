"""
Import the "Thermo ASA" range CSV (fixtures/design_lists/thermo_asa.csv) into
a new "Thermo ASA" collection under the existing "Thermo Laminates" category
(the category already backs the frontend's /asa-sheets route).

Unlike the design-index CSVs (thickness, design no, finish columns) this file
is a plain list of one product code per line, e.g.:

    9103 STONE
    GS 6004
    SN 5102

Each line is already the client's product name/code as-is, so it is used
verbatim (whitespace-normalized) for the product name/sku/slug — no column
reshuffling. Duplicate lines (e.g. "GS 6005" appears twice, "SN 5108" appears
with/without a space) are deduped.

No images yet, so products are created as --status (default: draft).

Idempotent: re-running updates rows already imported in place (matched by sku).

Usage:
    python manage.py import_thermo_asa --dry-run
    python manage.py import_thermo_asa
"""
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from catalog.models import Category, Collection, Product

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "design_lists"
CSV_FILE = "thermo_asa.csv"

CATEGORY_SLUG     = "thermo-laminates"
COLLECTION_NAME   = "Thermo ASA"
COLLECTION_SLUG   = "thermo-asa"

SHORT_DESC = "A weather-resistant Thermo ASA sheet from the Sanish Thermo ASA range — code {name}."

DESCRIPTION = (
    "<p>{name} is part of the Sanish <strong>Thermo ASA</strong> range — weather-resistant "
    "ASA sheets engineered for outdoor furniture, cladding and high-exposure architectural "
    "applications.</p>"
    "<p>Like every Sanish surface it is scratch resistant and easy to wipe clean. For exact "
    "colour and texture matching, request a physical sample or download the Thermo ASA "
    "catalogue from the catalogue page.</p>"
)

FEATURES = [
    "Weather Resistant",
    "UV Stable",
    "Scratch Resistant",
    "Easy to Clean",
]

LETTERS_DIGITS_RE = re.compile(r"^([A-Za-z]+)(\d.*)$")


def normalize_line(raw):
    """Collapse whitespace and insert a space between a letter prefix and a
    digit run with no space (e.g. "SN5108" -> "SN 5108")."""
    line = " ".join(raw.split())
    m = LETTERS_DIGITS_RE.match(line)
    if m:
        line = f"{m.group(1)} {m.group(2)}"
    return line.upper()


def split_code(name):
    """Best-effort split of a normalized line into (design_no, series) for
    tech-spec metadata only — does not affect the product name."""
    parts = name.split(" ", 1)
    if len(parts) == 2:
        a, b = parts
        return (a, b) if a.isdigit() else (b, a)
    return (name, "")


def parse_csv(path):
    seen = set()
    with open(path, encoding="utf-8-sig") as fh:
        for raw in fh:
            if not raw.strip():
                continue
            name = normalize_line(raw)
            if name in seen:
                continue
            seen.add(name)
            yield name


class Command(BaseCommand):
    help = "Import the Thermo ASA range CSV into a new 'Thermo ASA' collection."

    def add_arguments(self, parser):
        parser.add_argument("--dir", default=str(FIXTURES_DIR))
        parser.add_argument("--status", default="draft", choices=["draft", "published"],
                            help="Status for imported products (default: draft — no images yet)")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        path = Path(opts["dir"]) / CSV_FILE
        if not path.is_file():
            raise CommandError(f"Not found: {path}")

        names = list(parse_csv(path))
        self.stdout.write(f"{CSV_FILE}: {len(names)} unique product codes")

        if opts["dry_run"]:
            for n in names:
                self.stdout.write(f"  {n}  (slug={slugify(n)})")
            return

        try:
            category = Category.objects.get(slug=CATEGORY_SLUG)
        except Category.DoesNotExist:
            raise CommandError(f"Category '{CATEGORY_SLUG}' does not exist")

        status = opts["status"]
        created = updated = 0
        with transaction.atomic():
            collection, col_created = Collection.objects.get_or_create(
                slug=COLLECTION_SLUG,
                defaults={
                    "name": COLLECTION_NAME,
                    "status": Collection.STATUS_PUBLISHED,
                    "description": (
                        "Weather-resistant ASA sheets engineered for outdoor furniture, "
                        "cladding and high-exposure architectural applications."
                    ),
                },
            )
            self.stdout.write(f"Collection '{collection.slug}' "
                              f"({'created' if col_created else 'already existed'})")

            for name in names:
                design_no, series = split_code(name)
                sku = name
                product, is_new = Product.objects.get_or_create(
                    sku=sku, defaults={"name": name, "category": category}
                )
                product.name              = name
                product.category          = category
                product.collection        = collection
                product.status            = status
                product.surface           = "Thermo ASA Sheet"
                product.application       = "Outdoor Furniture, Cladding, Exterior Panels"
                product.short_description = SHORT_DESC.format(name=name)
                product.description       = DESCRIPTION.format(name=name)
                product.features          = list(FEATURES)
                product.tech_specs        = {
                    "Surface": "Thermo ASA Sheet",
                    "Design No": design_no,
                    "Series": series,
                    "Range": COLLECTION_NAME,
                }
                if not product.accent_color:
                    product.accent_color = "#85addc"
                if not product.slug:
                    product.slug = slugify(name)
                product.save()

                created += is_new
                updated += (not is_new)

        self.stdout.write(self.style.SUCCESS(
            f"Done — {created} created, {updated} updated. "
            f"All imported products are status='{status}' (no images yet)."
        ))
