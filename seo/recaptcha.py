"""Server-side Google reCAPTCHA v2/v3 verification against GlobalSEO settings."""
import requests

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


def verify_recaptcha(token, remote_ip=None):
    """Returns (ok, error_message). ok is True when reCAPTCHA is off (nothing
    to check) or when the token passes Google's verification (and, for v3,
    clears the configured minimum score)."""
    from seo.models import GlobalSEO

    settings = GlobalSEO.get()
    if settings.recaptcha_version == GlobalSEO.RECAPTCHA_OFF:
        return True, None

    if not settings.recaptcha_secret_key:
        return True, None

    if not token:
        return False, "reCAPTCHA verification is required."

    try:
        resp = requests.post(
            VERIFY_URL,
            data={"secret": settings.recaptcha_secret_key, "response": token, "remoteip": remote_ip},
            timeout=5,
        )
        result = resp.json()
    except (requests.RequestException, ValueError):
        return False, "Could not verify reCAPTCHA. Please try again."

    if not result.get("success"):
        return False, "reCAPTCHA verification failed. Please try again."

    if settings.recaptcha_version == GlobalSEO.RECAPTCHA_V3:
        score = result.get("score", 0)
        if score < float(settings.recaptcha_v3_min_score):
            return False, "reCAPTCHA verification failed. Please try again."

    return True, None
