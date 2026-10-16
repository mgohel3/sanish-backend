"""Instant storefront updates.

The Next.js storefront caches pages and CMS data for a few minutes. Whenever anything public is saved or deleted in the CMS we
POST to the storefront's /cms-revalidate endpoint so the next visitor gets fresh content straight away. Several saves in a row
(e.g. a product plus its image rows) are folded into one call ~1s later. Visitor-generated rows (inquiries, form submissions,
activity logs) never trigger it. Needs REVALIDATE_SECRET (same value in the storefront container); without it this is a no-op.
"""
import logging
import os
import threading
import urllib.request

from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save

log = logging.getLogger(__name__)

URL = os.environ.get("FRONTEND_REVALIDATE_URL", "http://frontend:3000/cms-revalidate")
DEBOUNCE_SECONDS = 1.0
WATCH_APPS = {"catalog", "media_library", "applications", "gallery", "pages", "homepage", "seo", "blog", "faq",
              "testimonials", "formbuilder", "menus"}
SKIP_MODELS = {"FormSubmission", "Inquiry", "Dealer", "ActivityLog"}

_lock = threading.Lock()
_timer = None


def _fire():
    secret = os.environ.get("REVALIDATE_SECRET", "")
    if not secret:
        log.warning("REVALIDATE_SECRET not set - storefront cache not refreshed")
        return
    req = urllib.request.Request(URL, method="POST", data=b"{}", headers={"x-revalidate-secret": secret, "Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as exc:  # the CMS save already succeeded; the storefront just falls back to its normal timer
        log.warning("storefront revalidate failed: %s", exc)


def _arm():
    global _timer
    with _lock:
        if _timer is not None:
            _timer.cancel()
        _timer = threading.Timer(DEBOUNCE_SECONDS, _fire)
        _timer.daemon = True
        _timer.start()


def _on_change(sender, **kwargs):
    if kwargs.get("raw"):  # fixture loading
        return
    transaction.on_commit(_arm)


def connect():
    from django.apps import apps

    for model in apps.get_models():
        if model._meta.app_label not in WATCH_APPS or model.__name__ in SKIP_MODELS:
            continue
        label = model._meta.label_lower
        post_save.connect(_on_change, sender=model, dispatch_uid=f"revalidate-save-{label}")
        post_delete.connect(_on_change, sender=model, dispatch_uid=f"revalidate-delete-{label}")
        for field in model._meta.many_to_many:
            m2m_changed.connect(_on_change, sender=field.remote_field.through, dispatch_uid=f"revalidate-m2m-{label}-{field.name}")
