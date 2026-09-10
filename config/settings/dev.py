"""Development settings — SQLite, debug toolbar, CDN Tailwind."""
import os
from .base import *  # noqa: F403

from dotenv import load_dotenv
load_dotenv()

DEBUG = True

# Required for {% if debug %} to be True in templates when accessing from localhost
INTERNAL_IPS = ["127.0.0.1", "localhost"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# Use local filesystem for media in dev
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

# Folders the Media Library "Import frontend images" button / `sync_media
# --import-frontend` pull from. Defaults to the sibling Next.js public image
# dirs when unset (see media_library.utils.get_import_dirs).
MEDIA_LIBRARY_IMPORT_DIRS = [
    str(BASE_DIR.parent / "sanish-next-fixed" / "public" / "assets" / "img"),  # noqa: F405
    str(BASE_DIR.parent / "sanish-next" / "public" / "assets" / "img"),        # noqa: F405
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Allow all for dev convenience
CORS_ALLOW_ALL_ORIGINS = True
