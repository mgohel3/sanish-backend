import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Inquiry

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Inquiry)
def notify_admins_of_new_inquiry(sender, instance, created, **kwargs):
    if not created:
        return

    from seo.models import SiteSettings
    site_settings = SiteSettings.get()

    recipients = site_settings.notify_email_list() or getattr(settings, "ADMIN_NOTIFY_EMAILS", [])
    if not recipients:
        return

    subject = f"New {instance.get_type_display()} Inquiry — {instance.name}"
    body = (
        "A new inquiry was submitted on the website.\n\n"
        f"Type:    {instance.get_type_display()}\n"
        f"Name:    {instance.name}\n"
        f"Email:   {instance.email}\n"
        f"Phone:   {instance.phone or '-'}\n"
        f"City:    {instance.city or '-'}\n"
        f"Page:    {instance.source_page or '-'}\n\n"
        f"Message:\n{instance.message or '-'}\n"
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
        logger.exception("Failed to send inquiry notification email for Inquiry #%s", instance.pk)
