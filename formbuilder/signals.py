import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import FormSubmission
from .services import send_auto_reply, send_webhook

logger = logging.getLogger(__name__)


@receiver(post_save, sender=FormSubmission)
def notify_admins_of_new_submission(sender, instance, created, **kwargs):
    if not created:
        return

    send_auto_reply(instance.form, instance.data)
    send_webhook(instance.form, instance.data, instance.source_page)

    from seo.models import SiteSettings
    site_settings = SiteSettings.get()

    recipients = (
        instance.form.notify_email_list()
        or site_settings.notify_email_list()
        or getattr(settings, "ADMIN_NOTIFY_EMAILS", [])
    )
    if not recipients:
        return

    lines = "\n".join(f"{k}: {v}" for k, v in (instance.data or {}).items())
    subject = f"New “{instance.form.name}” submission"
    body = (
        "A new form was submitted on the website.\n\n"
        f"Form: {instance.form.name}\n"
        f"Page: {instance.source_page or '-'}\n\n"
        f"{lines}\n"
    )

    from_email = site_settings.smtp_from_email or settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=recipients,
            fail_silently=False,
            connection=site_settings.get_email_connection(),
        )
    except Exception:
        logger.exception("Failed to send submission notification email for FormSubmission #%s", instance.pk)
