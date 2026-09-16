import json

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

# Small line-icon set for the block-type picker (dashboard/homepage/type_picker.html
# and dashboard/pages/type_picker.html). Purely presentational — keyed by
# ``homepage.blocks.BLOCK_TYPES`` key, with a generic fallback for anything new.
_BLOCK_ICONS = {
    "hero": '<path d="M3 6h18M3 12h18M3 18h10"/><path d="M17 15l3 3-3 3" stroke-width="1.5"/>',
    "about": '<rect x="3" y="4" width="8" height="16" rx="1"/><path d="M14 8h7M14 12h7M14 16h4"/>',
    "horizontal_showcase": '<rect x="2" y="6" width="6" height="12" rx="1"/><rect x="9" y="6" width="6" height="12" rx="1"/><rect x="16" y="6" width="6" height="12" rx="1"/>',
    "special_edition": '<path d="M12 2l2.4 6.6L21 11l-6.6 2.4L12 20l-2.4-6.6L3 11l6.6-2.4L12 2z"/>',
    "why_us": '<circle cx="12" cy="8" r="3"/><path d="M5 21v-2a7 7 0 0114 0v2"/>',
    "applications": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "rewards": '<path d="M20 7h-3.2a2.5 2.5 0 10-4.8-1 2.5 2.5 0 10-4.8 1H4a1 1 0 00-1 1v3h18V8a1 1 0 00-1-1z"/><path d="M3 12v7a1 1 0 001 1h16a1 1 0 001-1v-7"/><path d="M12 7v13"/>',
    "cta": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 10h8M8 14h5"/>',
    "cta_banner": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 10h8M8 14h5"/>',
    "blog_teaser": '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 8h8M8 12h8M8 16h4"/>',
    "rich_text": '<path d="M4 6h16M4 12h10M4 18h16"/>',
    "image_text": '<rect x="3" y="5" width="8" height="14" rx="1"/><path d="M14 8h7M14 12h7M14 16h4"/>',
    "page_hero": '<rect x="3" y="4" width="18" height="12" rx="1"/><path d="M3 20h18"/><circle cx="8" cy="9" r="1.5"/>',
    "content_section": '<rect x="3" y="4" width="7" height="16" rx="1"/><path d="M13 7h8M13 11h8M13 15h5"/>',
    "feature_cards": '<rect x="3" y="4" width="7" height="7" rx="1"/><rect x="14" y="4" width="7" height="7" rx="1"/><rect x="3" y="13" width="7" height="7" rx="1"/><rect x="14" y="13" width="7" height="7" rx="1"/>',
    "contact_details": '<path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014.1 2h3a2 2 0 012 1.7c.1.9.3 1.8.6 2.7a2 2 0 01-.5 2.1L8 9.7a16 16 0 006 6l1.2-1.2a2 2 0 012.1-.5c.9.3 1.8.5 2.7.6a2 2 0 011.7 2z"/>',
    "faq": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 015 .3c0 1.7-2.5 1.7-2.5 3.7" /><circle cx="12" cy="17" r=".2"/>',
    "testimonials": '<path d="M8 10h.01M12 10h.01M16 10h.01"/><path d="M4 4h16v11H8l-4 4V4z"/>',
    "gallery": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>',
    "team": '<circle cx="8" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M2 21v-1a6 6 0 0112 0v1"/><path d="M14 21v-1a5 5 0 016.5-4.8"/>',
    "pricing": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/><path d="M7 15h4"/>',
    "stats": '<path d="M4 20V10M11 20V4M18 20v-7"/>',
    "logos_strip": '<circle cx="6" cy="12" r="3"/><circle cx="18" cy="7" r="3"/><circle cx="18" cy="17" r="3"/><path d="M8.6 10.8l6.8-2.6M8.6 13.2l6.8 2.6"/>',
    "video_embed": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M10 9l5 3-5 3V9z"/>',
}
_BLOCK_ICON_FALLBACK = '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/>'


@register.filter
def block_icon(key):
    """Inline-SVG line icon for a home/page block-type key (see ``_BLOCK_ICONS``)."""
    inner = _BLOCK_ICONS.get(key, _BLOCK_ICON_FALLBACK)
    return mark_safe(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'class="w-6 h-6">' + inner + "</svg>"
    )


# Which wireframe layout (dashboard/_block_preview.html) best represents each
# block type's on-page structure — the Elementor-style "readymade block"
# thumbnail shown in the type pickers. Purely presentational.
_BLOCK_LAYOUTS = {
    "hero": "hero",
    "about": "split",
    "horizontal_showcase": "carousel",
    "special_edition": "feature",
    "why_us": "cards3",
    "applications": "grid4",
    "rewards": "split",
    "cta": "banner",
    "cta_banner": "banner",
    "blog_teaser": "carousel",
    "rich_text": "text",
    "image_text": "split",
    "page_hero": "banner",
    "content_section": "split",
    "feature_cards": "cards3",
    "contact_details": "split",
    "faq": "text",
    "testimonials": "cards3",
    "gallery": "grid4",
    "team": "cards3",
    "pricing": "cards3",
    "stats": "stats",
    "logos_strip": "logos",
    "video_embed": "video",
}


@register.filter
def block_layout(key):
    """Wireframe layout name for a block-type key — see ``_BLOCK_LAYOUTS``."""
    return _BLOCK_LAYOUTS.get(key, "text")


@register.filter
def dictkey(mapping, key):
    """Look up ``mapping[key]`` with a variable key (unsupported in the DTL)."""
    try:
        return mapping.get(key, "")
    except AttributeError:
        return ""


@register.filter
def jsonify(value, empty="[]"):
    """Compact JSON for embedding in an attribute (used to seed Alpine repeaters).

    Relies on Django's default autoescaping to turn embedded quotes into
    HTML entities — callers must NOT chain `|safe` after this, or a quote
    inside the data will close the attribute early and dump the rest of
    the tag's markup as visible page text.
    """
    if not value:
        return empty
    return json.dumps(value)


@register.filter
def jsonify_blank(subfields):
    """A blank row object for a repeater, given its list of sub-field specs."""
    blank = {}
    for sf in subfields or []:
        if sf.get("type") == "bool":
            blank[sf["name"]] = False
        elif sf.get("bool_select"):
            blank[sf["name"]] = False if sf.get("default") in (None, "", "false") else True
        else:
            blank[sf["name"]] = sf.get("default", "")
    return json.dumps(blank)


@register.filter
def cms_preview_src(path):
    """For displaying an image *inside the Django dashboard* (a different
    origin from the Next.js frontend). A path like "/assets/img/…" is
    relative to the FRONTEND's own public folder — the dashboard needs the
    frontend's origin prepended to actually load it as a thumbnail here.
    Anything else (a Django "/media/…" path, or an already-absolute URL) is
    same-origin for the dashboard already and is left untouched.
    Public API responses use `absolutize_media_urls` instead — this filter
    is for CMS-side previews only, it never touches stored data."""
    if not path:
        return ""
    if path.startswith(("http://", "https://", "//")):
        return path
    if path.startswith("/assets/"):
        return settings.FRONTEND_URL.rstrip("/") + path
    return path
