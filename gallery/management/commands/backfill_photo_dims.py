"""Measure every gallery photo's pixel size once, so the collage can reserve the right space for each
photo before it loads (no cropping, no jumping). Safe to re-run — only fills photos still missing a size.

  python manage.py backfill_photo_dims [--frontend http://frontend:3000]

Legacy photos live in the storefront's own /assets/ folder, so they are read over HTTP from the frontend
container; CMS uploads are read straight from the media folder.
"""
import io
import os
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image

from gallery.models import GalleryImage


class Command(BaseCommand):
    help = "Fill width/height for gallery photos that don't have them yet."

    def add_arguments(self, parser):
        parser.add_argument("--frontend", default="http://frontend:3000")

    def handle(self, *args, **opts):
        done = failed = 0
        for img in GalleryImage.objects.filter(width__isnull=True):
            path = img.image or ""
            try:
                if path.startswith(settings.MEDIA_URL):
                    with Image.open(os.path.join(str(settings.MEDIA_ROOT), path[len(settings.MEDIA_URL):])) as im:
                        w, h = im.size
                else:
                    url = path if path.startswith("http") else opts["frontend"].rstrip("/") + urllib.parse.quote(path)
                    with urllib.request.urlopen(url, timeout=20) as r:
                        data = r.read()
                    with Image.open(io.BytesIO(data)) as im:
                        w, h = im.size
                img.width, img.height = w, h
                img.save(update_fields=["width", "height"])
                done += 1
            except Exception as e:  # noqa: BLE001
                failed += 1
                self.stderr.write(f"  {img.pk} {path}: {e}")
        self.stdout.write(f"Measured {done} photo(s); {failed} failed.")
