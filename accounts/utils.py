import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_otp_email(user, code):
    """Email a login verification code to the user. Returns True on success."""
    from seo.models import SiteSettings
    site_settings = SiteSettings.get()
    from_email = site_settings.smtp_from_email or settings.DEFAULT_FROM_EMAIL

    subject = "Your Sanish CMS sign-in code"
    body = (
        f"Hi {user.get_full_name() or user.username},\n\n"
        f"Your verification code is: {code}\n\n"
        "This code expires in 10 minutes. If you did not try to sign in, "
        "you can safely ignore this email.\n"
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=False,
            connection=site_settings.get_email_connection(),
        )
        return True
    except Exception:
        logger.exception("Failed to send OTP email to user #%s", user.pk)
        return False
