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
        "name": "image_only", "type": "select", "label": "Banner type", "bool_select": True,
        "options": [
            {"value": "true", "label": "Image only — full-bleed photo, no text"},
            {"value": "false", "label": "Image + content — headline, copy & button"},
        ],
        "help": "Pick the layout first — it decides which image ratio to upload below.",
    },
    {
        "name": "image", "type": "image", "label": "Image (desktop)",
        "show_key": "image_only",
        "help_when_true": "Image only banner: use a 21:9 ratio image (e.g. 2400×1050px) — it fills the whole slide edge-to-edge with no text overlay.",
        "help_when_false": "Image + content banner: use a 16:9 ratio image (e.g. 1600×900px) — it sits in a rounded panel beside the headline and copy.",
    },
    {
        "name": "mobile_image", "type": "image", "label": "Image (mobile / portrait)",
        "help": "Optional — shown on phones instead of the desktop image. Recommended ratio 4:5 portrait (e.g. 1080×1350px). Falls back to the desktop image if left blank.",
    },
    {"name": "tag", "type": "text", "label": "Eyebrow tag", "hide_if": "image_only"},
    {"name": "line1", "type": "text", "label": "Headline line 1", "hide_if": "image_only"},
    {"name": "line2", "type": "text", "label": "Headline line 2", "hide_if": "image_only"},
    {"name": "sub", "type": "textarea", "label": "Sub copy", "hide_if": "image_only"},
    {"name": "cta_label", "type": "text", "label": "Primary button label", "hide_if": "image_only"},
    {"name": "cta_url", "type": "url", "label": "Primary button link", "hide_if": "image_only"},
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
            {"name": "slides", "type": "repeater", "label": "Slides", "fields": _HERO_SLIDE_FIELDS},
        ],
        "defaults": {
            "slides": [
                {
                    "image": "/assets/img/hero/slides/slide-1.jpg",
                    "mobile_image": "/assets/img/hero/slides/slide-1-mobile.jpg",
                    "tag": "Premium Craftsmanship",
                    "line1": "Surfaces That",
                    "line2": "Define Excellence",
                    "sub": "From decorative laminates to Thermo Laminates and architectural panels — 25+ years of craftsmanship behind every surface.",
                    "cta_label": "Explore Collection",
                    "cta_url": "/collection",
                    "image_only": True,
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
                    "image_only": False,
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
                    "image_only": False,
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
            {"name": "filters", "type": "repeater", "label": "Filter tabs", "fields": [
                {"name": "label", "type": "text", "label": "Label"},
            ]},
            {"name": "collections", "type": "repeater", "label": "Collections", "fields": [
                {"name": "name", "type": "text", "label": "Name"},
                {"name": "sub", "type": "text", "label": "Sub-label"},
                {"name": "category", "type": "text", "label": "Category (matches a filter tab)"},
                {"name": "image", "type": "image", "label": "Image"},
            ]},
        ],
        "defaults": {
            "heading": "Our Collections",
            "filters": [{"label": "Laminates"}, {"label": "Thermo Laminates"}],
            "collections": [
                {"name": "S'Shades", "sub": "Premium Finishes", "category": "Laminates", "image": "/assets/img/material/15-08-2026/Our Collections_Shades Collection.jpg"},
                {"name": "Thre3", "sub": "Exclusive Designs", "category": "Laminates", "image": "/assets/img/material/15-08-2026/Our Collections_Thre3 Collection.jpg"},
                {"name": "Perspective V4", "sub": "Durable Series", "category": "Thermo Laminates", "image": "/assets/img/material/15-08-2026/Our Collections_0.8mm Collection.jpg"},
                {"name": "Thermo", "sub": "Weather Resistant", "category": "Thermo Laminates", "image": "/assets/img/material/15-08-2026/thermocollection.jpg"},
                {"name": "Cool Colour", "sub": "Modern Shades", "category": "Louvers", "image": "/assets/img/material/15-08-2026/Our Collections_Cool Colour Collection.jpg"},
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
                {"title": "ISI Certified", "desc": "All our laminates conform to IS 2046 standards — guaranteed quality you can trust.", "icon": ""},
                {"title": "Scratch Resistant", "desc": "Our laminate surface is engineered to resist everyday scratches, scuffs, and abrasions.", "icon": ""},
                {"title": "Moisture Proof", "desc": "Formulated to withstand humid environments — perfect for kitchens and bathrooms.", "icon": ""},
                {"title": "Fire Retardant", "desc": "Formulated with fire-retardant properties for added safety in commercial applications.", "icon": ""},
                {"title": "Easy to Clean", "desc": "Stain-resistant topcoat — a simple wipe is all it takes to restore a pristine finish.", "icon": ""},
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
            "primary_url": "#",
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
        ],
        "defaults": {
            "eyebrow": "", "title": "", "description": "", "image": "", "image_fill": True,
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
    "rich_text", "image_text", "cta_banner", "testimonials", "gallery",
    "team", "pricing", "stats", "logos_strip", "video_embed",
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


def defaults_for(block_type: str) -> dict:
    cfg = BLOCK_TYPES.get(block_type)
    return dict(cfg["defaults"]) if cfg else {}
