"""
Declarative registry of home-page block types.

One entry per block type. Each entry drives three things:

* the CMS form  (``fields`` — rendered generically by templates/dashboard/homepage/form.html)
* the public API (``HomeSection.resolved()`` merges stored ``content`` over ``defaults``)
* the seed data (migration 0002 creates the current live sections with ``content={}``)

Field ``type`` values understood by the form template + view:

    text  textarea  richtext  url  image  number  bool  repeater

A ``repeater`` field carries its own ``fields`` list (one level deep) and is
posted back as a JSON string in a hidden ``<name>_json`` textarea — the same
convention dashboard/views/city_pages.py uses for ``why_choose_us_json`` etc.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Reusable sub-field groups
# ─────────────────────────────────────────────────────────────────────────────
_CTA_FIELDS = [
    {"name": "cta_label", "type": "text", "label": "Button label"},
    {"name": "cta_url", "type": "url", "label": "Button link"},
]

_HERO_SLIDE_FIELDS = [
    {
        "name": "hidden", "type": "bool",
        "label": "Hide this banner (stays here in the CMS, but is not shown on the website)",
    },
    {
        "name": "layout", "type": "select", "label": "Banner type", "default": "split",
        "options": [
            {"value": "split", "label": "Standard — text on the left, image on the right"},
            {"value": "stacked", "label": "Image on top (about 70%), text below (about 30%)"},
            {"value": "image_only", "label": "Image only — full-bleed photo, no text"},
            {"value": "video", "label": "Video banner — full-screen video with text on top"},
        ],
        "help": "Pick the layout first — it decides which image ratio to upload below.",
    },
    {
        "name": "image", "type": "image", "label": "Image (desktop)",
        "help_by_layout": {
            "split": "Standard banner: use a 16:9 ratio image (e.g. 1600×900px) — it sits in a rounded panel beside the headline and copy.",
            "stacked": "Image-on-top banner: use a wide image, about 21:9 (e.g. 2400×1000px) — it spans the full width above the text. Keep the subject in the middle.",
            "image_only": "Image only banner: use a 21:9 ratio image (e.g. 2400×1050px) — it fills the whole slide edge-to-edge with no text overlay.",
            "video": "Video banner: this is the poster — shown while the video loads and on devices that block autoplay. Use a still frame from the video, 16:9 (e.g. 1920×1080px).",
        },
    },
    {
        "name": "mobile_image", "type": "image", "label": "Image (mobile / portrait)",
        "help": "Optional — shown on phones instead of the desktop image. Recommended ratio 4:5 portrait (e.g. 1080×1350px). Falls back to the desktop image if left blank.",
    },
    {"name": "image_focus", "type": "select", "label": "Image focus point", "default": "center",
     "options": [{"value": "center", "label": "Centre"}, {"value": "left", "label": "Left"}, {"value": "right", "label": "Right"},
                 {"value": "top", "label": "Top"}, {"value": "bottom", "label": "Bottom"}, {"value": "left top", "label": "Top left"},
                 {"value": "right top", "label": "Top right"}, {"value": "left bottom", "label": "Bottom left"}, {"value": "right bottom", "label": "Bottom right"}],
     "help": "Which part of the picture stays visible when a small screen has to crop it. Use the side where the subject sits."},
    {"name": "fit_mode", "type": "select", "label": "Phones and tablets — picture", "default": "fill", "show_if": "layout", "show_value": "image_only",
     "options": [{"value": "fill", "label": "Fill the banner (crops the sides, keeps the focus point)"},
                 {"value": "fit", "label": "Show the whole picture (a blurred copy fills the gaps)"}]},
    {"name": "mobile_order", "type": "select", "label": "Phones and tablets — order", "default": "image_first", "show_if": "layout", "show_value": "split",
     "options": [{"value": "image_first", "label": "Image first, then text"}, {"value": "text_first", "label": "Text first, then image"}]},
    {"name": "swap_desktop", "type": "bool", "label": "On desktop: image on the left, text on the right", "show_if": "layout", "show_value": "split"},
    {"name": "video", "type": "video", "label": "Video (MP4) - use this Library button to upload or choose the video", "show_if": "layout", "show_value": "video",
     "help": "Plays automatically, muted and looping, behind the text. Use a short MP4 (H.264), 1920×1080, ideally under 8 MB — a long or heavy video slows the page down."},
    {"name": "text_align", "type": "select", "label": "Text position — left / centre / right", "default": "left", "show_if": "layout", "show_value": "video",
     "options": [{"value": "left", "label": "Left"}, {"value": "center", "label": "Centre"}, {"value": "right", "label": "Right"}]},
    {"name": "text_valign", "type": "select", "label": "Text position — top / middle / bottom", "default": "bottom", "show_if": "layout", "show_value": "video",
     "options": [{"value": "top", "label": "Top"}, {"value": "middle", "label": "Middle"}, {"value": "bottom", "label": "Bottom"}]},
    {"name": "overlay", "type": "select", "label": "Dark overlay behind the text", "default": "35", "show_if": "layout", "show_value": "video",
     "options": [{"value": "0", "label": "None"}, {"value": "20", "label": "Light"}, {"value": "35", "label": "Medium"}, {"value": "50", "label": "Strong"}, {"value": "65", "label": "Very strong"}],
     "help": "Darkens the video a little so white text stays readable."},
    {"name": "tag", "type": "text", "label": "Eyebrow tag", "styled": True, "hide_if": "layout", "hide_value": "image_only"},
    {"name": "line1", "type": "text", "label": "Headline line 1", "styled": True, "hide_if": "layout", "hide_value": "image_only"},
    {"name": "line2", "type": "text", "label": "Headline line 2", "styled": True, "hide_if": "layout", "hide_value": "image_only"},
    {"name": "sub", "type": "textarea", "label": "Sub copy", "styled": True, "hide_if": "layout", "hide_value": "image_only"},
    {"name": "cta_label", "type": "text", "label": "Primary button label", "styled": True, "hide_if": "layout", "hide_value": "image_only"},
    {"name": "cta_url", "type": "url", "label": "Primary button link", "hide_if": "layout", "hide_value": "image_only"},
]


# ─────────────────────────────────────────────────────────────────────────────
# Block registry
# ─────────────────────────────────────────────────────────────────────────────
BLOCK_TYPES: dict = {
    # ── Known home sections ────────────────────────────────────────────────
    "hero": {
        "label": "Hero Slider",
        "description": "Full-width rotating banner at the very top of the page.",
        "component": "Hero",
        "fields": [
            {"name": "slide_seconds", "type": "select", "label": "Slide speed (seconds each slide stays on screen)",
             "options": ["3", "4", "5", "6", "7", "8", "10", "12"],
             "help": "Lower = faster. 5 seconds is the default. The headline font, size and colour are set in the \"Text Style\" section at the bottom of this form."},
            {"name": "slides", "type": "repeater", "label": "Slides", "fields": _HERO_SLIDE_FIELDS},
        ],
        "defaults": {
            "slide_seconds": "5",
            "slides": [
                {
                    "image": "/assets/img/hero/slides/slide-1.jpg",
                    "mobile_image": "/assets/img/hero/slides/slide-1-mobile.jpg",
                    "tag": "Premium Craftsmanship",
                    "line1": "Surfaces That",
                    "line2": "Define Excellence",
                    "sub": "From decorative laminates to Thermo Laminates and architectural panels — 9+ years of craftsmanship behind every surface.",
                    "cta_label": "Explore Collection",
                    "cta_url": "/collection",
                    "layout": "image_only",
                    "hidden": False,
                },
                {
                    "image": "/assets/img/hero/slides/slide-2.jpg",
                    "mobile_image": "",
                    "tag": "Laminates Collection",
                    "line1": "Premium Laminates",
                    "line2": "For Every Space",
                    "sub": "High-gloss, matte and textured finishes crafted for architects, designers and luxury interiors — explore our complete laminates range.",
                    "cta_label": "Explore Collection",
                    "cta_url": "/collection",
                    "layout": "split",
                    "hidden": False,
                },
                {
                    "image": "/assets/img/hero/slides/slide-3.jpg",
                    "mobile_image": "",
                    "tag": "Thermo Laminates Collection",
                    "line1": "Built To Last",
                    "line2": "Thermo Panels",
                    "sub": "Engineered for UV and weather resistance — durable Thermo Laminate panels built for lasting performance on modern facades.",
                    "cta_label": "Explore Collection",
                    "cta_url": "/collection",
                    "layout": "split",
                    "hidden": False,
                },
                {
                    "image": "/assets/img/hero/slides/slide-2.jpg",
                    "mobile_image": "",
                    "tag": "",
                    "line1": "Image On Top,",
                    "line2": "Content Below",
                    "sub": "A banner layout with a large image above and a compact content strip beneath it.",
                    "cta_label": "Explore Collection",
                    "cta_url": "/collection",
                    "layout": "stacked",
                    "hidden": False,
                },
            ],
        },
    },

    "about": {
        "label": "About / Intro",
        "description": "Two-column intro with copy and a looping video or image.",
        "component": "About",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "body", "type": "richtext", "label": "Body copy"},
            {"name": "cta_label", "type": "text", "label": "Button label"},
            {"name": "cta_url", "type": "url", "label": "Button link"},
            {"name": "media_url", "type": "media", "label": "Video or image URL"},
        ],
        "defaults": {
            "heading": "Innovation That Shapes Modern Spaces",
            "body": (
                "<p>Founded in 2017, Sanish Laminates has emerged as one of India's fastest-growing "
                "premium laminate brands. Research-led quality and expressive design set us apart in "
                "the decorative surface industry.</p>"
                "<p>We continuously push boundaries to elevate interiors, bringing timeless appeal, "
                "durability and responsible manufacturing to every surface we create.</p>"
            ),
            "cta_label": "Read Our Story",
            "cta_url": "/about-us",
            "media_url": "https://videos.pexels.com/video-files/3163534/3163534-uhd_2560_1440_30fps.mp4",
        },
    },

    "horizontal_showcase": {
        "label": "Collections Showcase",
        "description": "Horizontal-scrolling strip of collection cards.",
        "component": "HorizontalShowcase",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "mobile_style", "type": "select", "label": "Style on phones and tablets", "default": "slider", "options": [
                {"value": "slider", "label": "Swipe slider (current)"},
                {"value": "strips", "label": "Expanding strips - one card open, others thin strips side by side"},
                {"value": "rows", "label": "Expanding rows - one card open, others stacked as slim rows"},
            ]},
            {"name": "desktop_style", "type": "select", "label": "Style on desktop", "default": "slider", "options": [
                {"value": "slider", "label": "Swipe slider (current)"},
                {"value": "strips", "label": "Expanding strips - one card open, others thin strips side by side"},
            ]},
            {"name": "autoplay_seconds", "type": "select", "label": "Auto-advance - seconds before the next card opens", "default": "4", "options": [
                {"value": "0", "label": "Off - only change when someone taps or swipes"},
                {"value": "2", "label": "2 seconds (fast)"},
                {"value": "3", "label": "3 seconds"},
                {"value": "4", "label": "4 seconds (default)"},
                {"value": "5", "label": "5 seconds"},
                {"value": "6", "label": "6 seconds"},
                {"value": "8", "label": "8 seconds"},
                {"value": "10", "label": "10 seconds (slow)"},
            ]},
            {"name": "filters", "type": "repeater", "label": "Filter tabs", "fields": [
                {"name": "label", "type": "text", "label": "Label"},
            ]},
            {"name": "collections", "type": "repeater", "label": "Collections", "fields": [
                {"name": "name", "type": "text", "label": "Name"},
                {"name": "sub", "type": "text", "label": "Sub-label"},
                {"name": "category", "type": "text", "label": "Category (matches a filter tab)"},
                {"name": "image", "type": "image", "label": "Image"},
                {"name": "link", "type": "url", "label": "Link - page this card opens (optional, e.g. /laminates?collection=thre3 or /asa-sheets)"},
            ]},
        ],
        "defaults": {
            "heading": "Our Collections",
            "mobile_style": "slider",
            "desktop_style": "slider",
            "autoplay_seconds": "4",
            "filters": [{"label": "Laminates"}, {"label": "Thermo Laminates"}],
            "collections": [
                {"name": "S'Shades", "link": "/laminates?collection=sshades", "sub": "Premium Finishes", "category": "Laminates", "image": "/assets/img/material/15-08-2026/Our Collections_Shades Collection.jpg"},
                {"name": "Thre3", "link": "/laminates?collection=thre3", "sub": "Exclusive Designs", "category": "Laminates", "image": "/assets/img/material/15-08-2026/Our Collections_Thre3 Collection.jpg"},
                {"name": "Cool Colour", "link": "/laminates?collection=cool-colour", "sub": "Modern Shades", "category": "Laminates", "image": "/assets/img/material/15-08-2026/Our Collections_Cool Colour Collection.jpg"},
                {"name": "Perspective V4", "link": "/laminates?collection=08mm", "sub": "Durable Series", "category": "Laminates", "image": "/assets/img/material/15-08-2026/Our Collections_0.8mm Collection.jpg"},
                {"name": "Thermo Laminates", "link": "/asa-sheets", "sub": "Weather Resistant", "category": "Thermo Laminates", "image": "/assets/img/material/15-08-2026/thermocollection.jpg"},
            ],
        },
    },

    "special_edition": {
        "label": "Special Edition",
        "description": "Feature block with parallax image and tag pills.",
        "component": "SpecialEdition",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading (use a line break for two lines)"},
            {"name": "body", "type": "textarea", "label": "Body copy"},
            {"name": "tags", "type": "repeater", "label": "Tag pills", "fields": [
                {"name": "label", "type": "text", "label": "Label"},
            ]},
            {"name": "cta_label", "type": "text", "label": "Button label"},
            {"name": "cta_url", "type": "url", "label": "Button link"},
            {"name": "image", "type": "image", "label": "Image"},
            {"name": "image_kicker", "type": "text", "label": "Image overline"},
            {"name": "image_title", "type": "text", "label": "Image caption title"},
        ],
        "defaults": {
            "heading": "Special Edition\nArchitectural Panels",
            "body": "Our limited edition architectural panels redefine luxury interiors. Featuring synchronised textures that perfectly mimic natural materials with enhanced durability.",
            "tags": [{"label": "Syncro-Texture"}, {"label": "1.25 mm Thick"}, {"label": "8ft × 4ft"}, {"label": "Moisture Proof"}],
            "cta_label": "Explore Range",
            "cta_url": "/collection",
            "image": "/assets/img/material/15-08-2026/Special Edition_Banner.jpg",
            "image_kicker": "Limited Collection",
            "image_title": "Syncro-Texture Series",
        },
    },

    "why_us": {
        "label": "Why Us (carousel)",
        "description": "Sliding cards of product benefits.",
        "component": "WhyUsCarousel",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading (HTML allowed for <em>)"},
            {"name": "cards", "type": "repeater", "label": "Cards", "fields": [
                {"name": "title", "type": "text", "label": "Title"},
                {"name": "desc", "type": "textarea", "label": "Description"},
                {"name": "icon", "type": "image", "label": "Icon (optional)"},
            ]},
        ],
        "defaults": {
            "heading": "Built to Last. <em>Designed to Impress.</em>",
            "cards": [
                {"title": "ISI Certified", "desc": "All our laminates conform to IS 2046 standards — guaranteed quality you can trust.", "icon": "/assets/img/icon/why-us/isi-certified.svg"},
                {"title": "Scratch Resistant", "desc": "Our laminate surface is engineered to resist everyday scratches, scuffs, and abrasions.", "icon": "/assets/img/icon/why-us/scratch-resistant.svg"},
                {"title": "Moisture Proof", "desc": "Formulated to withstand humid environments — perfect for kitchens and bathrooms.", "icon": "/assets/img/icon/why-us/moisture-proof.svg"},
                {"title": "Fire Retardant", "desc": "Formulated with fire-retardant properties for added safety in commercial applications.", "icon": "/assets/img/icon/why-us/fire-retardant.svg"},
                {"title": "Easy to Clean", "desc": "Stain-resistant topcoat — a simple wipe is all it takes to restore a pristine finish.", "icon": "/assets/img/icon/why-us/easy-to-clean.svg"},
            ],
        },
    },

    "applications": {
        "label": "Applications Gallery",
        "description": "Heading + link over a gallery tile grid (tiles stay auto-populated).",
        "component": "Applications",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "cta_label", "type": "text", "label": "Link label"},
            {"name": "cta_url", "type": "url", "label": "Link URL"},
        ],
        "defaults": {
            "heading": "Architectural Applications",
            "cta_label": "View all applications",
            "cta_url": "/applications",
        },
    },

    "rewards": {
        "label": "Rewards App",
        "description": "S'Rewards app promo with perks grid and store badges.",
        "component": "RewardsHighlight",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "body", "type": "textarea", "label": "Body copy"},
            {"name": "cta_label", "type": "text", "label": "Link label"},
            {"name": "cta_url", "type": "url", "label": "Link URL"},
            {"name": "perks", "type": "repeater", "label": "Perks", "fields": [
                {"name": "label", "type": "text", "label": "Label"},
                {"name": "desc", "type": "textarea", "label": "Description"},
                {"name": "icon", "type": "image", "label": "Icon"},
            ]},
        ],
        "defaults": {
            "heading": "S'Rewards App",
            "body": "Join thousands of carpenters and contractors already earning with Sanish. Download the S'Rewards app and start turning every purchase into points, gifts, and cash rewards.",
            "cta_label": "Learn more about the programme →",
            "cta_url": "/rewards",
            "perks": [
                {"label": "Earn Points", "desc": "Earn reward points on every purchase of Sanish products.", "icon": "/assets/img/icon/rewards-earn-points.svg"},
                {"label": "Exclusive Offers", "desc": "Unlock member-only discounts, gifts, and seasonal promotions.", "icon": "/assets/img/icon/rewards-exclusive-offers.svg"},
                {"label": "Track Rewards", "desc": "Real-time tracking of your points balance and redemption history.", "icon": "/assets/img/icon/rewards-track-rewards.svg"},
                {"label": "Easy Redemption", "desc": "Redeem points instantly for cash discounts on your next order.", "icon": "/assets/img/icon/rewards-easy-redemption.svg"},
            ],
        },
    },

    "cta": {
        "label": "Closing CTA Banner",
        "description": "Full-width parallax-image call to action near the footer.",
        "component": "CTA",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading (use a line break for two lines)"},
            {"name": "body", "type": "textarea", "label": "Body copy"},
            {"name": "bg_image", "type": "image", "label": "Background image"},
            {"name": "primary_label", "type": "text", "label": "Primary button label"},
            {"name": "primary_url", "type": "url", "label": "Primary button link"},
            {"name": "secondary_label", "type": "text", "label": "Secondary button label"},
            {"name": "secondary_url", "type": "url", "label": "Secondary button link"},
        ],
        "defaults": {
            "heading": "Elevate Your Next\nArchitectural Project",
            "body": "Contact our design consultants to explore the complete Sanish Laminates collection and discuss your bespoke requirements.",
            "bg_image": "/assets/img/cta-bg.jpg",
            "primary_label": "View Catalogue",
            "primary_url": "/collection",
            "secondary_label": "Contact Sales Team",
            "secondary_url": "mailto:info@sanishlaminate.com",
        },
    },

    "blog_teaser": {
        "label": "Editorial / Blog Teaser",
        "description": "Heading + link over the latest blog posts.",
        "component": "Blog",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "cta_label", "type": "text", "label": "Link label"},
            {"name": "cta_url", "type": "url", "label": "Link URL"},
        ],
        "defaults": {
            "heading": "Editorial",
            "cta_label": "View all articles",
            "cta_url": "/blog",
        },
    },

    # ── Generic reusable blocks ──────────────────────────────────────────────
    "rich_text": {
        "label": "Rich Text",
        "description": "A heading and free-form formatted copy.",
        "component": "RichTextBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "body", "type": "richtext", "label": "Body"},
            {"name": "align", "type": "select", "label": "Alignment", "options": ["left", "center"]},
        ],
        "defaults": {"heading": "", "body": "", "align": "left"},
    },

    "image_text": {
        "label": "Image + Text",
        "description": "Two-column block: image on one side, copy on the other.",
        "component": "ImageTextBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "body", "type": "richtext", "label": "Body"},
            {"name": "image", "type": "image", "label": "Image"},
            {"name": "image_side", "type": "select", "label": "Image side", "options": ["left", "right"]},
            {"name": "cta_label", "type": "text", "label": "Button label"},
            {"name": "cta_url", "type": "url", "label": "Button link"},
        ],
        "defaults": {"heading": "", "body": "", "image": "", "image_side": "left", "cta_label": "", "cta_url": ""},
    },

    "cta_banner": {
        "label": "CTA Banner",
        "description": "Generic full-width call-to-action band with up to two buttons.",
        "component": "CtaBannerBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "sub", "type": "textarea", "label": "Sub copy"},
            {"name": "bg_image", "type": "image", "label": "Background image (optional)"},
            {"name": "primary_label", "type": "text", "label": "Primary button label"},
            {"name": "primary_url", "type": "url", "label": "Primary button link"},
            {"name": "secondary_label", "type": "text", "label": "Secondary button label"},
            {"name": "secondary_url", "type": "url", "label": "Secondary button link"},
        ],
        "defaults": {
            "heading": "", "sub": "", "bg_image": "",
            "primary_label": "", "primary_url": "",
            "secondary_label": "", "secondary_url": "",
        },
    },

    # ── Generic inner-page blocks (used by the Pages builder) ───────────────
    "page_hero": {
        "label": "Page Hero",
        "description": "Banner at the top of an inner page — eyebrow, title, sub copy over an image.",
        "component": "PageHero",
        "fields": [
            {"name": "eyebrow", "type": "text", "label": "Eyebrow"},
            {"name": "title", "type": "text", "label": "Title"},
            {"name": "description", "type": "textarea", "label": "Sub copy"},
            {"name": "image", "type": "image", "label": "Background image"},
            {"name": "image_fill", "type": "bool", "label": "Full-bleed image background"},
            {"name": "image_below_header", "type": "bool", "label": "Centre image in the visible banner (below the header)"},
        ],
        "defaults": {
            "eyebrow": "", "title": "", "description": "", "image": "", "image_fill": True, "image_below_header": False,
        },
    },

    "content_section": {
        "label": "Content Section",
        "description": "Eyebrow + heading + rich-text body, optionally beside an image.",
        "component": "ContentSectionBlock",
        "fields": [
            {"name": "eyebrow", "type": "text", "label": "Eyebrow"},
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "body", "type": "richtext", "label": "Body"},
            {"name": "image", "type": "image", "label": "Image (optional)"},
            {"name": "image_side", "type": "select", "label": "Image side", "options": ["right", "left", "none"]},
        ],
        "defaults": {
            "eyebrow": "", "heading": "", "body": "", "image": "", "image_side": "right",
        },
    },

    "feature_cards": {
        "label": "Feature Cards",
        "description": "A heading over a grid of image + title + text cards (certifications, perks, mission…).",
        "component": "FeatureCardsBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "sub", "type": "textarea", "label": "Sub copy"},
            {"name": "columns", "type": "select", "label": "Columns", "options": ["3", "2", "4"]},
            {"name": "cards", "type": "repeater", "label": "Cards", "fields": [
                {"name": "title", "type": "text", "label": "Title"},
                {"name": "subtitle", "type": "text", "label": "Subtitle"},
                {"name": "body", "type": "textarea", "label": "Body"},
                {"name": "image", "type": "image", "label": "Image / icon"},
                {"name": "accent", "type": "text", "label": "Accent colour (hex)"},
            ]},
        ],
        "defaults": {"heading": "", "sub": "", "columns": "3", "cards": []},
    },

    "contact_details": {
        "label": "Contact Details",
        "description": "Headquarters address / phone / email list beside an embedded map.",
        "component": "ContactDetailsBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "address", "type": "textarea", "label": "Address"},
            {"name": "phones", "type": "repeater", "label": "Phone numbers", "fields": [
                {"name": "label", "type": "text", "label": "Display"},
                {"name": "value", "type": "text", "label": "tel: value"},
            ]},
            {"name": "emails", "type": "repeater", "label": "Emails", "fields": [
                {"name": "value", "type": "text", "label": "Email"},
            ]},
            {"name": "map_embed_url", "type": "url", "label": "Google Maps embed URL"},
            {"name": "form_heading", "type": "text", "label": "Form heading"},
            {"name": "form_sub", "type": "textarea", "label": "Form sub copy"},
            {"name": "form_slug", "type": "text", "label": "CMS form slug (optional)",
             "help": "Leave blank to keep the built-in enquiry form. Set to a Forms slug to render that CMS-managed form instead."},
        ],
        "defaults": {
            "heading": "Our Headquarters", "address": "", "phones": [], "emails": [],
            "map_embed_url": "", "form_heading": "Post your requirements", "form_sub": "",
            "form_slug": "",
        },
    },

    "faq": {
        "label": "FAQ",
        "description": "Heading over an expandable question / answer list.",
        "component": "FaqBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "items", "type": "repeater", "label": "Questions", "fields": [
                {"name": "q", "type": "text", "label": "Question"},
                {"name": "a", "type": "textarea", "label": "Answer"},
            ]},
        ],
        "defaults": {"heading": "Frequently asked questions", "items": []},
    },

    # ── Ready-made library blocks — drop into any page ──────────────────────
    "testimonials": {
        "label": "Testimonials",
        "description": "Heading over a grid of customer quotes.",
        "component": "TestimonialsBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "sub", "type": "textarea", "label": "Sub copy"},
            {"name": "items", "type": "repeater", "label": "Testimonials", "fields": [
                {"name": "quote", "type": "textarea", "label": "Quote"},
                {"name": "name", "type": "text", "label": "Name"},
                {"name": "role", "type": "text", "label": "Role / company"},
                {"name": "avatar", "type": "image", "label": "Photo (optional)"},
            ]},
        ],
        "defaults": {"heading": "What our customers say", "sub": "", "items": []},
    },

    "gallery": {
        "label": "Image Gallery",
        "description": "Heading over a responsive grid of images.",
        "component": "GalleryBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "sub", "type": "textarea", "label": "Sub copy"},
            {"name": "columns", "type": "select", "label": "Columns", "options": ["3", "2", "4"]},
            {"name": "images", "type": "repeater", "label": "Images", "fields": [
                {"name": "image", "type": "image", "label": "Image"},
                {"name": "caption", "type": "text", "label": "Caption (optional)"},
            ]},
        ],
        "defaults": {"heading": "", "sub": "", "columns": "3", "images": []},
    },

    # ---- Rewards-page blocks (also reusable on any page) -------------------
    "rewards_intro": {
        "label": "Intro with App Card",
        "description": "Heading and two paragraphs on the left (with Google Play / App Store badges) beside a dark app card with a stats grid.",
        "component": "RewardsIntroBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "body_1", "type": "textarea", "label": "Paragraph 1"},
            {"name": "body_2", "type": "textarea", "label": "Paragraph 2"},
            {"name": "show_store_badges", "type": "bool", "label": "Show app-store badges"},
            {"name": "card_eyebrow", "type": "text", "label": "Card small label"},
            {"name": "card_title", "type": "textarea", "label": "Card title", "help": "Press Enter for a new line."},
            {"name": "stats", "type": "repeater", "label": "Card stats", "fields": [
                {"name": "val", "type": "text", "label": "Value"},
                {"name": "label", "type": "text", "label": "Label"},
            ]},
        ],
        "defaults": {
            "heading": "You Install, We Reward",
            "body_1": "As a professional carpenter, you are the backbone of every beautiful interior. The Sanish Rewards programme is our way of saying thank you. Every laminate sheet you install earns you points that convert into real cash, gift vouchers, and exclusive perks.",
            "body_2": "Join thousands of carpenters across India who are already earning with Sanish. Simply download the app, scan packs and watch your rewards grow.",
            "show_store_badges": True,
            "card_eyebrow": "Sanish Rewards",
            "card_title": "Carpenter\nLoyalty App",
            "stats": [
                {"val": "10,000+", "label": "Active Carpenters"},
                {"val": "₹50L+", "label": "Rewards Paid Out"},
                {"val": "5★", "label": "App Rating"},
                {"val": "Free", "label": "To Join"},
            ],
        },
    },

    "steps_cards": {
        "label": "Numbered Steps (How It Works)",
        "description": "Heading over a row of numbered cards with a coloured top bar — good for 'how it works' or process steps.",
        "component": "StepsCardsBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "steps", "type": "repeater", "label": "Steps", "fields": [
                {"name": "num", "type": "text", "label": "Number / label", "help": "e.g. 01"},
                {"name": "title", "type": "text", "label": "Title"},
                {"name": "desc", "type": "textarea", "label": "Description"},
                {"name": "accent", "type": "text", "label": "Accent colour", "help": "Hex colour such as #fabf7d — used for the top bar and number."},
            ]},
        ],
        "defaults": {
            "heading": "How It Works",
            "steps": [
                {"num": "01", "title": "Download & Register", "desc": "Download the Sanish Rewards app from Google Play and create your free account in minutes.", "accent": "#fabf7d"},
                {"num": "02", "title": "Install & Earn Points", "desc": "Install Sanish Laminates at your projects. Scan the QR code on each pack to instantly credit points to your account.", "accent": "#ac8cc0"},
                {"num": "03", "title": "Redeem Your Rewards", "desc": "Accumulate points and redeem them for cash transfers, gift vouchers, tools, and exclusive offers — all inside the app.", "accent": "#f39ba2"},
            ],
        },
    },

    "icon_benefits": {
        "label": "Benefits Grid (icon cards)",
        "description": "Heading over a grid of cards, each with a coloured icon, title and short text.",
        "component": "IconBenefitsBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "items", "type": "repeater", "label": "Cards", "fields": [
                {"name": "icon", "type": "select", "label": "Icon", "options": [
                    {"value": "user", "label": "Person"}, {"value": "star", "label": "Star"},
                    {"value": "card", "label": "Card / payment"}, {"value": "chart", "label": "Chart"},
                    {"value": "gift", "label": "Gift"}, {"value": "phone", "label": "Phone / support"},
                    {"value": "shield", "label": "Shield"}, {"value": "heart", "label": "Heart"},
                    {"value": "bolt", "label": "Lightning"}, {"value": "check", "label": "Tick"},
                ]},
                {"name": "title", "type": "text", "label": "Title"},
                {"name": "desc", "type": "textarea", "label": "Description"},
                {"name": "accent", "type": "text", "label": "Accent colour", "help": "Hex colour such as #85addc."},
            ]},
        ],
        "defaults": {
            "heading": "What You Get",
            "items": [
                {"icon": "user", "title": "Made for Carpenters", "desc": "Exclusively designed for professional carpenters and furniture makers who use Sanish products daily.", "accent": "#fabf7d"},
                {"icon": "star", "title": "Points on Every Pack", "desc": "Earn reward points on every Sanish laminate pack you install. The more you install, the more you earn.", "accent": "#ac8cc0"},
                {"icon": "card", "title": "Instant Cash Transfer", "desc": "Redeem your points directly to your bank account or UPI ID — no waiting, no paperwork.", "accent": "#f39ba2"},
                {"icon": "chart", "title": "Track Live Earnings", "desc": "See your points balance, transaction history and available rewards in real-time through the app.", "accent": "#85addc"},
                {"icon": "gift", "title": "Exclusive Gift Vouchers", "desc": "Redeem points for gift vouchers from leading brands — tools, home appliances, shopping & more.", "accent": "#fabf7d"},
                {"icon": "phone", "title": "Dedicated Support", "desc": "Our team is available to assist with any questions about your points, redemptions or app issues.", "accent": "#ac8cc0"},
            ],
        },
    },

    "client_testimonials": {
        "label": "Client Testimonials (carousel)",
        "description": "The sliding testimonials carousel. The people and quotes are managed in Dashboard › Testimonials (add, hide, reorder there) — this block only sets the heading, so you can drop it on any page.",
        "component": "ClientTestimonialsBlock",
        "fields": [
            {"name": "category", "type": "select", "label": "Testimonial category", "dynamic_options": "testimonial_categories",
             "help": "Which list to show. Manage the lists (and add new categories) in Dashboard › Testimonials."},
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "sub", "type": "textarea", "label": "Sub copy (optional)"},
        ],
        "defaults": {"category": "Clients", "heading": "What Our Clients Say", "sub": ""},
    },

    "faq_cards": {
        "label": "FAQ Cards",
        "description": "Heading over a narrow list of question-and-answer cards (all answers visible).",
        "component": "FaqCardsBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "items", "type": "repeater", "label": "Questions", "fields": [
                {"name": "q", "type": "text", "label": "Question"},
                {"name": "a", "type": "textarea", "label": "Answer"},
            ]},
        ],
        "defaults": {
            "heading": "Frequently Asked",
            "items": [
                {"q": "Who can join the Sanish Rewards programme?", "a": "Any professional carpenter or furniture maker who regularly purchases and installs Sanish Laminates is eligible to join. Registration is free."},
                {"q": "How do I earn points?", "a": "Scan the unique QR code found on each Sanish laminate pack using the app. Points are instantly credited to your account after verification."},
                {"q": "When can I redeem my points?", "a": "You can redeem points once you reach the minimum threshold. Redemptions are processed within 24–48 hours to your bank or UPI."},
                {"q": "Is there an expiry on points?", "a": "Points are valid for 12 months from the date of earning. Stay active and keep installing to retain and grow your balance."},
            ],
        },
    },

    "app_cta": {
        "label": "App Download CTA (dark)",
        "description": "Dark call-to-action: small label, big heading, paragraph, app-store badges and a row of tick points.",
        "component": "AppCtaBlock",
        "fields": [
            {"name": "eyebrow", "type": "text", "label": "Small label"},
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "text", "type": "textarea", "label": "Paragraph"},
            {"name": "show_store_badges", "type": "bool", "label": "Show app-store badges"},
            {"name": "checks", "type": "repeater", "label": "Tick points", "fields": [
                {"name": "text", "type": "text", "label": "Text"},
            ]},
        ],
        "defaults": {
            "eyebrow": "Start Earning Today",
            "heading": "Download the App & Join Free",
            "text": "Over 10,000 carpenters are already earning with Sanish Rewards. Register in 2 minutes and start collecting points on your very next installation.",
            "show_store_badges": True,
            "checks": [{"text": "Free to join"}, {"text": "Instant points"}, {"text": "No minimum order"}],
        },
    },

    "media_gallery": {
        "label": "Events & Media Gallery",
        "description": "Photos and videos from events and meetups — filter tabs per event, 24 per page, click to open in a viewer.",
        "component": "MediaGalleryBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "sub", "type": "textarea", "label": "Sub copy"},
            {"name": "columns", "type": "select", "label": "Columns", "options": ["3", "2", "4"]},
            {"name": "album_order", "type": "text", "ui": "hidden", "label": "Album order"},
            {"name": "items", "type": "repeater", "ui": "media_grid", "label": "Photos & videos", "fields": [
                {"name": "image", "type": "image", "label": "Photo (or cover image for a video)"},
                {"name": "video", "type": "video", "label": "Video (optional)",
                 "help": "Leave blank for a photo. For a video: pick an uploaded MP4 with Library, or paste a YouTube / Vimeo link "
                         "(links have no size limit — best for long event films)."},
                {"name": "caption", "type": "text", "label": "Caption (optional)"},
                {"name": "alt", "type": "text", "label": "Alt text (SEO)"},
                {"name": "category", "type": "text", "label": "Event / album (optional)",
                 "help": "Items with the same name are grouped under one filter tab, e.g. “Carpenter Meet 2026”."},
            ]},
        ],
        "defaults": {"heading": "", "sub": "", "columns": "3", "album_order": "", "items": []},
    },

    "media_teaser": {
        "label": "Media Gallery (preview + button)",
        "description": "A grid of recent photos and videos from the Events & Media page, with a button to open the full media gallery.",
        "component": "MediaTeaser",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "sub", "type": "textarea", "label": "Sub copy (optional)"},
            {"name": "count", "type": "select", "label": "How many items to show", "options": ["6", "3", "4", "8"]},
            {"name": "cta_label", "type": "text", "label": "Button label"},
            {"name": "cta_url", "type": "url", "label": "Button link (the full media gallery page)"},
            {"name": "source_page", "type": "text", "label": "Take the photos/videos from this page (its Events & Media Gallery block)",
             "help": 'Page address without the slash, e.g. "events".'},
        ],
        "defaults": {
            "heading": "Media Gallery",
            "sub": "Moments from our events, exhibitions and carpenter meetups.",
            "count": "6",
            "cta_label": "View Media Gallery \u2192",
            "cta_url": "/events",
            "source_page": "events",
        },
    },

    "team": {
        "label": "Team",
        "description": "Heading over a grid of team member photo + name + role + bio.",
        "component": "TeamBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "sub", "type": "textarea", "label": "Sub copy"},
            {"name": "columns", "type": "select", "label": "Columns", "options": ["3", "4", "2"]},
            {"name": "members", "type": "repeater", "label": "Members", "fields": [
                {"name": "photo", "type": "image", "label": "Photo"},
                {"name": "name", "type": "text", "label": "Name"},
                {"name": "role", "type": "text", "label": "Role"},
                {"name": "bio", "type": "textarea", "label": "Bio (optional)"},
            ]},
        ],
        "defaults": {"heading": "Meet the team", "sub": "", "columns": "3", "members": []},
    },

    "pricing": {
        "label": "Pricing Table",
        "description": "Heading over a row of pricing / plan cards.",
        "component": "PricingBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading"},
            {"name": "sub", "type": "textarea", "label": "Sub copy"},
            {"name": "plans", "type": "repeater", "label": "Plans", "fields": [
                {"name": "title", "type": "text", "label": "Plan name"},
                {"name": "price", "type": "text", "label": "Price"},
                {"name": "period", "type": "text", "label": "Billing period (e.g. /month)"},
                {"name": "features", "type": "textarea", "label": "Features (one per line)"},
                {"name": "cta_label", "type": "text", "label": "Button label"},
                {"name": "cta_url", "type": "url", "label": "Button link"},
                {"name": "highlighted", "type": "bool", "label": "Highlight this plan"},
            ]},
        ],
        "defaults": {"heading": "Pricing", "sub": "", "plans": []},
    },

    "stats": {
        "label": "Stats Strip",
        "description": "A row of big numbers with labels (e.g. years in business, projects completed).",
        "component": "StatsBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading (optional)"},
            {"name": "stats", "type": "repeater", "label": "Stats", "fields": [
                {"name": "value", "type": "text", "label": "Value (e.g. 10,000+)"},
                {"name": "label", "type": "text", "label": "Label"},
            ]},
        ],
        "defaults": {"heading": "", "stats": []},
    },

    "logos_strip": {
        "label": "Logos Strip",
        "description": "A row of partner / certification / press logos.",
        "component": "LogosStripBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading (optional)"},
            {"name": "logos", "type": "repeater", "label": "Logos", "fields": [
                {"name": "image", "type": "image", "label": "Logo"},
                {"name": "name", "type": "text", "label": "Name (alt text)"},
            ]},
        ],
        "defaults": {"heading": "Trusted by", "logos": []},
    },

    "video_embed": {
        "label": "Video",
        "description": "An embedded YouTube / Vimeo video with an optional heading and caption.",
        "component": "VideoEmbedBlock",
        "fields": [
            {"name": "heading", "type": "text", "label": "Heading (optional)"},
            {"name": "video_url", "type": "url", "label": "Video URL (YouTube / Vimeo)"},
            {"name": "caption", "type": "text", "label": "Caption (optional)"},
        ],
        "defaults": {"heading": "", "video_url": "", "caption": ""},
    },
}


# Blocks that make sense to add more than once / freely (shown first in picker)
GENERIC_BLOCKS = ["rich_text", "image_text", "cta_banner"]

# Blocks the frontend's generic SitePage renderer (sanish-next-fixed
# PageBlockRenderer.PAGE_BLOCK_REGISTRY) actually knows how to draw. The
# other entries in BLOCK_TYPES (hero, about, horizontal_showcase, …) are
# home-page-only components that don't exist as standalone page blocks —
# picking one of them for a custom/inner page silently renders nothing.
INNER_PAGE_BLOCKS = [
    "page_hero", "content_section", "feature_cards", "faq", "contact_details",
    "rich_text", "image_text", "cta_banner", "testimonials", "gallery", "media_gallery",
    "team", "pricing", "stats", "logos_strip", "video_embed",
    "rewards_intro", "steps_cards", "icon_benefits", "client_testimonials", "faq_cards", "app_cta",
]

# Order the 8 currently-live sections are seeded in
SEED_ORDER = [
    ("hero", "Hero Slider", True),
    ("about", "About / Intro", True),
    ("horizontal_showcase", "Collections Showcase", True),
    ("special_edition", "Special Edition", True),
    ("why_us", "Why Us", True),
    ("applications", "Applications Gallery", True),
    ("rewards", "Rewards App", True),
    ("cta", "Closing CTA Banner", True),
    ("blog_teaser", "Editorial / Blog Teaser", False),  # hidden today
]


def block_choices():
    return [(key, cfg["label"]) for key, cfg in BLOCK_TYPES.items()]


def with_dynamic_options(cfg):
    """Copy of a block config with any ``dynamic_options`` select filled from the database."""
    if not cfg:
        return cfg
    import copy
    out = copy.deepcopy(cfg)
    for f in out.get("fields", []):
        if f.get("dynamic_options") == "testimonial_categories":
            from testimonials.models import TestimonialCategory
            f["options"] = list(TestimonialCategory.objects.values_list("name", flat=True))
    return out


def defaults_for(block_type: str) -> dict:
    cfg = BLOCK_TYPES.get(block_type)
    return dict(cfg["defaults"]) if cfg else {}
