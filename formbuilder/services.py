"""
Routes a validated form submission to wherever ``FormDefinition.target_pipeline``
says it belongs. Keeps the public submit endpoint generic while letting a form
that used to be hard-coded (Contact, the site-wide popup, …) feed the exact
same ``leads.Inquiry`` pipeline / Leads dashboard it always has.
"""
import json
import logging
import re
import urllib.request
from urllib.error import URLError

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")

WEBHOOK_TIMEOUT_SECONDS = 6

# Field names that map straight onto Inquiry columns. Anything else in the
# submitted data is folded into the Inquiry's ``message`` as "Label: value"
# lines — the same trick the hard-coded ContactForm/Popup already used for
# their pincode/enquire_type fields.
_DIRECT_INQUIRY_FIELDS = ("name", "email", "phone", "city")


def _render_template(template: str, context: dict) -> str:
    return _TOKEN_RE.sub(lambda m: str(context.get(m.group(1), "")), template or "")


def send_auto_reply(form, data: dict):
    """Email the person who submitted ``form`` a CMS-authored confirmation, if enabled."""
    if not form.auto_reply_enabled:
        return

    data = data or {}
    email_field = next((f for f in form.fields.all() if f.field_type == "email"), None)
    to_email = (data.get(email_field.name) if email_field else None) or data.get("email")
    if not to_email:
        return

    from django.conf import settings
    from django.core.mail import send_mail
    from seo.models import SiteSettings

    site_settings = SiteSettings.get()
    context = {**data, "email": to_email, "name": data.get("name", ""), "site_name": site_settings.site_name}

    subject = _render_template(form.auto_reply_subject, context) or f"Thanks for contacting {site_settings.site_name}"
    body = _render_template(form.auto_reply_body, context)
    from_email = site_settings.smtp_from_email or settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
            connection=site_settings.get_email_connection(),
        )
    except Exception:
        logger.exception("Failed to send auto-reply email for form %s", form.slug)


def send_webhook(form, data: dict, source_page: str = ""):
    """POST a submission of ``form`` as JSON to its configured webhook URL, if enabled."""
    if not form.webhook_enabled or not form.webhook_url:
        return

    from django.utils import timezone

    payload = {
        "form": form.slug,
        "form_name": form.name,
        "submitted_at": timezone.now().isoformat(),
        "source_page": source_page or "",
        "data": data or {},
    }
    headers = {"Content-Type": "application/json"}
    if form.webhook_secret:
        headers["X-Webhook-Secret"] = form.webhook_secret

    request = urllib.request.Request(
        form.webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        urllib.request.urlopen(request, timeout=WEBHOOK_TIMEOUT_SECONDS)
    except (URLError, ValueError, OSError):
        logger.exception("Failed to deliver webhook for form %s to %s", form.slug, form.webhook_url)


def route_submission_to_inquiry(form, data: dict, source_page: str):
    """Create a ``leads.Inquiry`` from a CMS form submission and return it.
    Triggers the existing new-inquiry notification signal unchanged."""
    from leads.models import Inquiry

    valid_types = {choice for choice, _ in Inquiry.TYPE_CHOICES}
    inquiry_type = data.get("type") if data.get("type") in valid_types else None
    inquiry_type = inquiry_type or (form.inquiry_type if form.inquiry_type in valid_types else Inquiry.TYPE_CONTACT)

    fields_by_name = {f.name: f for f in form.fields.all()}
    direct = {key: "" for key in _DIRECT_INQUIRY_FIELDS}
    message_lines = []

    for name, value in data.items():
        if name in direct:
            direct[name] = value or ""
        elif name == "type":
            continue
        elif name == "message":
            if value:
                message_lines.insert(0, str(value))
        elif value not in (None, ""):
            label = fields_by_name[name].label if name in fields_by_name else name
            message_lines.append(f"{label}: {value}")

    inquiry = Inquiry.objects.create(
        type=inquiry_type,
        form=form,
        name=direct["name"],
        email=direct["email"],
        phone=direct["phone"],
        city=direct["city"],
        message="\n".join(message_lines),
        source_page=source_page or "",
    )
    send_auto_reply(form, data)
    send_webhook(form, data, source_page)
    return inquiry
