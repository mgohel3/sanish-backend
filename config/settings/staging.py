"""
Staging settings — single-VPS Docker deploy.

Differs from prod.py: PostgreSQL in a local container (no SSL), media on a
local Docker volume instead of Cloudflare R2, runs behind an nginx TLS proxy.
Swap to R2 later by setting the R2_* env vars and switching the storage block
back to the S3 backend (see prod.py).
"""
import os

import dj_database_url

from .base import *  # noqa: F403

# ── Core ──────────────────────────────────────────────────────────────────────
DEBUG = False
SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "staging.sanishlaminate.com").split(",")
    if h.strip()
]

# ── Database (local container Postgres) ──────────────────────────────────────
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ["DATABASE_URL"],
        conn_max_age=600,
        ssl_require=False,
    )
}

# ── Media (local volume, served by nginx at /media/) ─────────────────────────
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
MEDIA_URL = "/media/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", str(BASE_DIR / "media"))  # noqa: F405

# ── Behind nginx TLS ────────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CSRF_TRUSTED_ORIGINS", "https://staging.sanishlaminate.com"
    ).split(",")
    if o.strip()
]
# HSTS stays off on staging so the subdomain isn't pinned to HTTPS during setup.
SECURE_HSTS_SECONDS = 0

# ── CORS ────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CORS_ALLOWED_ORIGINS", "https://staging.sanishlaminate.com"
    ).split(",")
    if o.strip()
]

# ── Email ──────────────────────────────────────────────────────────────────
# base.py reads EMAIL_* from the environment. If no SMTP host is configured,
# fall back to console output so inquiry-notification signals don't error.
if not os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── Logging ────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
