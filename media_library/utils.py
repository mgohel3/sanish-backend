"""WebP conversion utility using Pillow."""
import io
import os
import shutil
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile


def convert_to_webp(asset):
    """
    Converts an image MediaAsset to WebP format.
    Returns the relative path of the saved WebP file, or None on failure.
    """
    try:
        from PIL import Image
        from django.core.files.storage import default_storage

        # Open via storage backend (works for both local and R2)
        with default_storage.open(asset.file.name) as f:
            img = Image.open(f)
            img.load()

        # Convert RGBA → RGB for JPEG-based WebP compat
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

        # Also capture dimensions while we have the image open
        if not asset.width or not asset.height:
            from media_library.models import MediaAsset
            MediaAsset.objects.filter(pk=asset.pk).update(
                width=img.width, height=img.height
            )

        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=82, method=4)
        buf.seek(0)

        base = os.path.splitext(os.path.basename(asset.file.name))[0]
        webp_name = f"media/webp/{base}.webp"

        saved = default_storage.save(webp_name, ContentFile(buf.read()))
        return saved

    except Exception:
        return None


# ── Library sync helpers ────────────────────────────────────────────────────────

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif", ".bmp", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm", ".mkv", ".m4v"}
DOC_EXTS   = {".pdf"}
ALLOWED_EXTS = IMAGE_EXTS | VIDEO_EXTS | DOC_EXTS

# Directories under MEDIA_ROOT that are managed by the app, not user content.
_SKIP_DIRS = {"webp", "cache", "__pycache__", "tmp"}


def _title_from_filename(name):
    stem = os.path.splitext(name)[0]
    return stem.replace("-", " ").replace("_", " ").strip().title()[:300]


def scan_media_root():
    """
    Walk MEDIA_ROOT and register any on-disk file that has no MediaAsset row yet.
    Returns (added, skipped). Never deletes or modifies existing rows.
    """
    from .models import MediaAsset

    media_root = Path(settings.MEDIA_ROOT)
    if not media_root.is_dir():
        return 0, 0

    known = set(
        MediaAsset.objects.exclude(file="").values_list("file", flat=True)
    )
    added = skipped = 0

    for root, dirs, files in os.walk(media_root):
        dirs[:] = [d for d in dirs if d.lower() not in _SKIP_DIRS]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in ALLOWED_EXTS:
                continue
            abs_path = Path(root) / fname
            rel_path = abs_path.relative_to(media_root).as_posix()
            # Skip generated webp derivatives
            if rel_path.startswith("media/webp/") or "/webp/" in rel_path:
                continue
            if rel_path in known:
                skipped += 1
                continue
            asset = MediaAsset(
                file=rel_path,
                title=_title_from_filename(fname),
                original_filename=fname,
            )
            asset.save()
            known.add(rel_path)
            added += 1

    return added, skipped


def import_external_dir(source_dir, folder_name=None, dest_subdir="imported"):
    """
    Copy every supported media file from `source_dir` (recursively) into
    MEDIA_ROOT/<dest_subdir>/<source-name>/... and register a MediaAsset for
    each. Files already imported (same destination path) are skipped.

    Returns (added, skipped).
    """
    from .models import MediaAsset, MediaFolder

    source = Path(source_dir)
    if not source.is_dir():
        return 0, 0

    media_root = Path(settings.MEDIA_ROOT)
    label = source.name
    dest_root = media_root / dest_subdir / label

    folder = None
    if folder_name:
        folder, _ = MediaFolder.objects.get_or_create(name=folder_name)

    known = set(
        MediaAsset.objects.exclude(file="").values_list("file", flat=True)
    )
    added = skipped = 0

    for root, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in ALLOWED_EXTS:
                continue
            abs_src = Path(root) / fname
            rel_inner = abs_src.relative_to(source)
            abs_dest = dest_root / rel_inner
            rel_path = abs_dest.relative_to(media_root).as_posix()

            if rel_path in known or abs_dest.exists():
                skipped += 1
                if rel_path not in known and abs_dest.exists():
                    # File on disk but no row — let scan pick it up instead.
                    pass
                continue

            abs_dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(abs_src, abs_dest)
            except Exception:
                continue

            asset = MediaAsset(
                file=rel_path,
                title=_title_from_filename(fname),
                original_filename=fname,
                folder=folder,
            )
            asset.save()
            known.add(rel_path)
            added += 1

    return added, skipped


def get_import_dirs():
    """Configured external directories to import from (see settings.MEDIA_LIBRARY_IMPORT_DIRS)."""
    dirs = getattr(settings, "MEDIA_LIBRARY_IMPORT_DIRS", None)
    if dirs:
        return [Path(d) for d in dirs]
    # Sensible default: sibling Next.js frontends' public image folders.
    base = Path(settings.BASE_DIR).parent
    return [
        base / "sanish-next-fixed" / "public" / "assets" / "img",
        base / "sanish-next" / "public" / "assets" / "img",
    ]


def absolutize_media_urls(data, request):
    """
    Recursively rewrite stored ``MEDIA_URL`` paths (e.g. ``/media/…``) inside an
    arbitrary JSON-ish structure into absolute URLs, so the storefront — which
    runs on a different origin (localhost:3000) than this API (localhost:8000) —
    can load CMS-hosted images and video.

    Values that are already absolute (``http…``, protocol-relative, or a
    non-media path like ``/assets/…`` served by the frontend itself) are left
    untouched. In production ``MEDIA_URL`` is the full S3/R2 endpoint, so stored
    values are already absolute and ``build_absolute_uri`` returns them as-is.
    """
    media_url = settings.MEDIA_URL
    if request is None or not media_url:
        return data

    if isinstance(data, str):
        if media_url.startswith(("http://", "https://", "//")):
            return data  # prod: values already absolute
        if data.startswith(media_url):
            return request.build_absolute_uri(data)
        return data
    if isinstance(data, list):
        return [absolutize_media_urls(v, request) for v in data]
    if isinstance(data, dict):
        return {k: absolutize_media_urls(v, request) for k, v in data.items()}
    return data
