"""
Signed, short-lived tokens that let the CMS "Preview" button open the real
Next.js frontend page for a draft/unpublished item, instead of a hand-built
mock. The frontend passes the token back on `?preview=<token>` and the
corresponding `*PreviewDetailView` (api/views.py) verifies it before serving
an item regardless of `status`.

Deliberately not a JWT / DB-backed session — this only ever needs to answer
"did our own CMS mint this link in the last few hours", so a plain signed,
timestamped value (HMAC'd with SECRET_KEY) is enough and needs no migration.
"""
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

PREVIEW_MAX_AGE_SECONDS = 6 * 60 * 60  # 6 hours — one CMS editing session


def make_preview_token(kind: str, pk: int) -> str:
    """`kind` namespaces the token to its model ('product', 'blogpost', …) so a
    token minted for one preview endpoint can't be replayed against another."""
    signer = TimestampSigner(salt=f"cms-preview:{kind}")
    return signer.sign(str(pk))


def verify_preview_token(kind: str, pk: int, token: str) -> bool:
    if not token:
        return False
    signer = TimestampSigner(salt=f"cms-preview:{kind}")
    try:
        value = signer.unsign(token, max_age=PREVIEW_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return False
    return value == str(pk)
