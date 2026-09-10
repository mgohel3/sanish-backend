"""
Import the 101 legacy blog posts from the old PHP site backup.

Backup layout (see its README.md):
    <dir>/blogs.json                 - metadata per post (slug, meta, date, poster_image)
    <dir>/posts_html/<slug>.html     - clean body HTML per post
    <dir>/images_all_blog_folder/    - every hero image file

Usage:
    python manage.py import_legacy_blog "F:/.../blog-backup"
    python manage.py import_legacy_blog "<dir>" --dry-run
    python manage.py import_legacy_blog "<dir>" --limit 5
    python manage.py import_legacy_blog "<dir>" --images skip
    python manage.py import_legacy_blog "<dir>" --emit-redirects redirects.json

Idempotent: re-running update_or_create()s by slug and reuses the media asset.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify

from accounts.models import User
from blog.models import BlogCategory, BlogPost
from media_library.models import MediaAsset, MediaFolder

LEGACY_HOST_RE = re.compile(r"https?://(?:www\.)?sanishlaminate\.com/([A-Za-z0-9\-/]+)")
TITLE_SUFFIX_RE = re.compile(r"\s*[-|–]\s*Sanish\s+Laminates?\s*$", re.I)

# Category buckets — matched against the post title + heading text only
# (meta_keywords on the old site are boilerplate spam and useless for this).
CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Kitchen Laminates",   ("kitchen", "countertop", "cabinet")),
    ("Wardrobe Laminates",  ("wardrobe", "closet")),
    ("Laminate Doors",      ("door",)),
    ("High Gloss & Acrylic", ("gloss", "acrylic")),
    ("Veneer Laminates",    ("veneer",)),
    ("HPL Sheets",          ("high pressure", "high-pressure", "hpl")),
    ("Wood Laminates",      ("wood laminate", "woodgrain", "wood-look", "wood look", "oak", "walnut")),
    ("Care & Maintenance",  ("clean", "maintain", "maintenance", "spotless")),
    ("Buying Guide",        ("buy ", "online", "supplier", "top 10", "top 50", "brands in india")),
]
FALLBACK_CATEGORY = "Laminates"


def clean_title(page_title: str, body_html: str) -> str:
    t = (page_title or "").strip()
    t = TITLE_SUFFIX_RE.sub("", t).strip()
    if " | " in t:  # drop trailing "| keyword-stuffed clause" from the old meta title
        t = t.split(" | ", 1)[0].strip()
    if not t:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", body_html, re.I | re.S)
        if m:
            t = strip_tags(m.group(1)).strip()
    return t


def clean_body(raw: str, title: str) -> str:
    """Drop the doctype/meta/<title>/<h1> preamble and a leading duplicated-title <h2>."""
    body = re.sub(r"(?is)^.*?</h1>\s*", "", raw, count=1)
    if "</h1>" not in raw:  # safety: no <h1>, just strip the head tags
        body = re.sub(r"(?is)^\s*<!doctype[^>]*>\s*", "", raw)
        body = re.sub(r"(?is)^\s*<meta[^>]*>\s*", "", body)
        body = re.sub(r"(?is)^\s*<title>.*?</title>\s*", "", body)

    m = re.match(r"(?is)\s*<h2[^>]*>(.*?)</h2>\s*", body)
    if m:
        norm = lambda s: re.sub(r"\s+", " ", strip_tags(s)).strip().lower()
        if norm(m.group(1)) == norm(title):
            body = body[m.end():]

    # Rewrite legacy absolute links -> new /blog/<slug> route
    body = LEGACY_HOST_RE.sub(lambda mo: "/blog/" + mo.group(1).strip("/"), body)
    return body.strip()


def guess_categories(title: str, headings: list[str]) -> list[str]:
    # Title only — old-site headings/keywords are too noisy and over-tag everything.
    hay = title.lower()
    hits = [name for name, kws in CATEGORY_RULES if any(k in hay for k in kws)]
    return hits or [FALLBACK_CATEGORY]


class Command(BaseCommand):
    help = "Import legacy blog posts from the old PHP site backup folder."

    def add_arguments(self, parser):
        parser.add_argument("backup_dir", help="Path to the blog-backup folder")
        parser.add_argument("--dry-run", action="store_true", help="Parse and report, write nothing")
        parser.add_argument("--limit", type=int, default=0, help="Only import the first N posts")
        parser.add_argument(
            "--images", choices=["media", "skip"], default="media",
            help="media = copy each hero into the Media Library and link it (default); skip = no images",
        )
        parser.add_argument("--author", default="", help="Username to set as author (default: first superuser)")
        parser.add_argument("--emit-redirects", default="", help="Write a Next.js redirects JSON array to this path")

    def handle(self, *args, **opts):
        backup = Path(opts["backup_dir"])
        if not backup.is_dir():
            raise CommandError(f"Not a directory: {backup}")
        meta_path = backup / "blogs.json"
        html_dir = backup / "posts_html"
        img_dir = backup / "images_all_blog_folder"
        if not meta_path.is_file():
            raise CommandError(f"Missing {meta_path}")
        if not html_dir.is_dir():
            raise CommandError(f"Missing {html_dir}")

        posts = json.loads(meta_path.read_text(encoding="utf-8"))
        if opts["limit"]:
            posts = posts[: opts["limit"]]

        author = None
        if opts["author"]:
            author = User.objects.filter(username=opts["author"]).first()
            if not author:
                raise CommandError(f"No user named {opts['author']!r}")
        author = author or User.objects.filter(is_superuser=True).order_by("id").first()

        dry = opts["dry_run"]
        do_images = opts["images"] == "media" and not dry
        folder = None
        if do_images:
            folder, _ = MediaFolder.objects.get_or_create(slug="blog-heroes", defaults={"name": "Blog Heroes"})

        created = updated = skipped_img = 0
        cat_cache: dict[str, BlogCategory] = {}
        redirects: list[dict] = []

        for i, p in enumerate(posts, 1):
            slug = p["slug"].strip()
            raw_html = (html_dir / f"{slug}.html").read_text(encoding="utf-8") if (html_dir / f"{slug}.html").is_file() else ""
            if not raw_html:
                self.stderr.write(self.style.WARNING(f"  [{i}] {slug}: no body HTML, skipping"))
                continue

            title = clean_title(p.get("page_title") or p.get("list_title") or slug, raw_html)
            body = clean_body(raw_html, title)
            cats = guess_categories(title, p.get("headings"))

            try:
                pub = timezone.make_aware(datetime.strptime(p["published"], "%d.%m.%Y"))
            except Exception:
                pub = None

            redirects.append({"source": f"/{slug}", "destination": f"/blog/{slug}", "permanent": True})

            self.stdout.write(f"  [{i:>3}] {slug}")
            self.stdout.write(f"        title: {title}")
            self.stdout.write(f"        date : {p.get('published')}  cats: {', '.join(cats)}")
            if dry:
                continue

            with transaction.atomic():
                post, is_new = BlogPost.objects.update_or_create(
                    slug=slug,
                    defaults=dict(
                        title=title,
                        content=body,
                        status=BlogPost.STATUS_PUBLISHED,
                        seo_title=(p.get("meta_title") or "")[:255],
                        meta_description=(p.get("meta_description") or "")[:320],
                        meta_keywords=(p.get("meta_keywords") or "")[:500],
                        published_at=pub,
                        author=author,
                        layout=BlogPost.LAYOUT_SIDEBAR,
                        show_author=True, show_share=True, show_related=True,
                    ),
                )
                # categories
                cat_objs = []
                for name in cats:
                    c = cat_cache.get(name)
                    if not c:
                        c, _ = BlogCategory.objects.get_or_create(
                            slug=slugify(name), defaults={"name": name}
                        )
                        cat_cache[name] = c
                    cat_objs.append(c)
                post.categories.set(cat_objs)

                # hero image -> Media Library
                if do_images and not post.featured_image_id:
                    fname = Path(p.get("poster_image", "")).name
                    src = img_dir / fname
                    if src.is_file():
                        existing = MediaAsset.objects.filter(original_filename=fname, folder=folder).first()
                        if existing:
                            post.featured_image = existing
                        else:
                            with src.open("rb") as fh:
                                asset = MediaAsset(
                                    folder=folder, type=MediaAsset.TYPE_IMAGE,
                                    alt_text=title[:300], title=title[:300],
                                    original_filename=fname, uploaded_by=author,
                                )
                                asset.file.save(f"blog/{fname}", File(fh), save=True)
                            post.featured_image = asset
                        post.save(update_fields=["featured_image"])
                    else:
                        skipped_img += 1
                        self.stderr.write(self.style.WARNING(f"        image missing: {fname}"))

                # backdate created so the listing orders chronologically
                if pub:
                    BlogPost.objects.filter(pk=post.pk).update(created=pub)

            created += is_new
            updated += (not is_new)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"{'DRY RUN — ' if dry else ''}created {created}, updated {updated}, images missing {skipped_img}"
        ))

        if opts["emit_redirects"]:
            Path(opts["emit_redirects"]).write_text(json.dumps(redirects, indent=2), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Wrote {len(redirects)} redirects -> {opts['emit_redirects']}"))
