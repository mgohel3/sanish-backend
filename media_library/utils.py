"""WebP conversion utility using Pillow."""
import io
import os
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
