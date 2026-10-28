"""Branded HTML version of the CMS-authored auto-reply: the editor's text on top, a signature block (logo + contact details) below."""
import html

BRAND = "#A58BC7"
INK = "#1f2230"
MUTED = "#6b6b80"


def _paragraphs(text: str) -> str:
    out = []
    for block in (text or "").replace("\r\n", "\n").split("\n\n"):
        block = block.strip()
        if block:
            out.append(
                f'<p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:{INK};">'
                + html.escape(block).replace("\n", "<br>")
                + "</p>"
            )
    return "".join(out)


def render_auto_reply_html(body_text: str, s, details=(), cta=None) -> str:
    """``s`` is the SiteSettings row; ``body_text`` the already-rendered auto-reply body."""
    site = "https://sanishlaminate.com"
    cta_label, cta_url = cta or ("Explore our collections", f"{site}/collection")
    logo = f"{site}/media/email/logo.png"
    name = html.escape(s.site_name or "Sanish Laminates")
    links = [
        (label, url)
        for label, url in (
            ("Instagram", s.instagram_url), ("Facebook", s.facebook_url),
            ("YouTube", s.youtube_url), ("LinkedIn", s.linkedin_url),
        )
        if url
    ]
    social = " &nbsp;·&nbsp; ".join(
        f'<a href="{html.escape(u)}" style="color:{MUTED};text-decoration:none;">{l}</a>' for l, u in links
    )
    quote = ""
    if details:
        rows = "".join(
            f'<div style="margin-top:6px;"><span style="color:{INK};font-weight:bold;">{html.escape(l)}:</span> '
            + html.escape(v[:600]).replace("\n", "<br>") + "</div>"
            for l, v in details
        )
        quote = (
            f'<div style="margin:6px 0 20px;padding:14px 18px;background:#f6f3fa;border-left:3px solid {BRAND};'
            f'border-radius:6px;font-size:13px;line-height:1.6;color:{MUTED};">'
            f'<div style="font-size:11px;letter-spacing:.12em;text-transform:uppercase;">Your enquiry</div>{rows}</div>'
        )
    contact = []
    if s.phone_primary:
        contact.append(f'<a href="tel:{html.escape(s.phone_primary.replace(" ", ""))}" style="color:{INK};text-decoration:none;">{html.escape(s.phone_primary)}</a>')
    if s.email_primary:
        contact.append(f'<a href="mailto:{html.escape(s.email_primary)}" style="color:{INK};text-decoration:none;">{html.escape(s.email_primary)}</a>')
    contact.append(f'<a href="{site}" style="color:{BRAND};text-decoration:none;">sanishlaminate.com</a>')
    address = html.escape(s.full_address()) if s.full_address() else ""
    return f"""<!doctype html>
<html><body style="margin:0;padding:0;background:#f4f2f7;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f2f7;padding:28px 12px;">
<tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:14px;overflow:hidden;font-family:Helvetica,Arial,sans-serif;">
<tr><td style="height:5px;background:{BRAND};font-size:0;line-height:0;">&nbsp;</td></tr>
<tr><td style="padding:32px 36px 8px;">
{_paragraphs(body_text)}{quote}
<p style="margin:0 0 26px;"><a href="{html.escape(cta_url)}" style="display:inline-block;background:{BRAND};color:#ffffff;text-decoration:none;font-size:13px;font-weight:bold;letter-spacing:.08em;text-transform:uppercase;padding:13px 26px;border-radius:999px;">{html.escape(cta_label)}</a></p>
</td></tr>
<tr><td style="padding:0 36px 30px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #ebe8f0;">
<tr><td style="padding-top:22px;">
<img src="{logo}" alt="{name}" width="150" style="display:block;border:0;height:auto;margin-bottom:12px;">
<div style="font-size:13px;line-height:1.8;color:{INK};">{" &nbsp;|&nbsp; ".join(contact)}</div>
{f'<div style="font-size:12px;line-height:1.6;color:{MUTED};margin-top:4px;">{address}</div>' if address else ""}
{f'<div style="font-size:12px;margin-top:10px;">{social}</div>' if social else ""}
</td></tr></table>
</td></tr>
</table>
<div style="max-width:600px;font-family:Helvetica,Arial,sans-serif;font-size:11px;line-height:1.6;color:#9a98a6;padding:14px 8px;text-align:center;">You are receiving this because you contacted {name} through our website.</div>
</td></tr></table>
</body></html>"""
