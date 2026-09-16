"""
Ready-made page templates — Elementor/WordPress-theme style starting points
for a brand-new :class:`SitePage`. Each template is just an ordered list of
blocks (from ``homepage.blocks.BLOCK_TYPES``) with light placeholder content,
so a new page opens already laid out instead of blank; every block is fully
editable/removable afterwards exactly like any other page's blocks.

Adding a template is additive only — it never touches existing pages.
"""

PAGE_TEMPLATES = {
    "blank": {
        "label": "Blank Page",
        "description": "No starter blocks — build it up yourself from the block picker.",
        "blocks": [],
    },

    "landing": {
        "label": "Landing Page",
        "description": "Hero, intro, feature cards, testimonials and a closing call-to-action.",
        "blocks": [
            ("page_hero", "Hero", "", {
                "eyebrow": "Introducing",
                "title": "Your Page Title",
                "description": "A short, compelling sub-headline goes here.",
                "image": "", "image_fill": True,
            }),
            ("content_section", "Intro", "", {
                "eyebrow": "About This",
                "heading": "Tell your story",
                "body": "<p>Write an introduction to this page here. Explain what it's about and why it matters to your visitor.</p>",
                "image": "", "image_side": "right",
            }),
            ("feature_cards", "Highlights", "", {
                "heading": "Why it matters",
                "sub": "",
                "columns": "3",
                "cards": [
                    {"title": "Highlight One", "subtitle": "", "accent": "#85addc", "image": "", "body": "Describe the first key point here."},
                    {"title": "Highlight Two", "subtitle": "", "accent": "#f39ba2", "image": "", "body": "Describe the second key point here."},
                    {"title": "Highlight Three", "subtitle": "", "accent": "#ac8cc0", "image": "", "body": "Describe the third key point here."},
                ],
            }),
            ("testimonials", "Testimonials", "", {
                "heading": "What people say",
                "sub": "",
                "items": [
                    {"quote": "Replace this with a real customer quote.", "name": "Customer Name", "role": "Role / Company", "avatar": ""},
                ],
            }),
            ("cta_banner", "Closing CTA", "", {
                "heading": "Ready to get started?",
                "sub": "Add a closing call-to-action here.",
                "bg_image": "", "primary_label": "Contact Us", "primary_url": "/contact-us",
                "secondary_label": "", "secondary_url": "",
            }),
        ],
    },

    "about_style": {
        "label": "About / Story Page",
        "description": "Hero, content section, feature cards (mission/values-style) and a closing CTA — the same shape as About Us.",
        "blocks": [
            ("page_hero", "Hero", "", {
                "eyebrow": "About", "title": "Your Page Title",
                "description": "A short sub-headline about this page.",
                "image": "", "image_fill": True,
            }),
            ("content_section", "Story", "", {
                "eyebrow": "Our Story", "heading": "Tell your story",
                "body": "<p>Write your story or introduction here.</p>",
                "image": "", "image_side": "right",
            }),
            ("feature_cards", "Values", "", {
                "heading": "Our values", "sub": "", "columns": "3",
                "cards": [
                    {"title": "Value One", "subtitle": "", "accent": "#85addc", "image": "", "body": "Describe this value."},
                    {"title": "Value Two", "subtitle": "", "accent": "#f39ba2", "image": "", "body": "Describe this value."},
                    {"title": "Value Three", "subtitle": "", "accent": "#ac8cc0", "image": "", "body": "Describe this value."},
                ],
            }),
            ("cta_banner", "Closing CTA", "", {
                "heading": "Want to know more?", "sub": "",
                "bg_image": "", "primary_label": "Contact Us", "primary_url": "/contact-us",
                "secondary_label": "", "secondary_url": "",
            }),
        ],
    },

    "services": {
        "label": "Services / Pricing Page",
        "description": "Hero, feature cards, pricing table, FAQ and a closing CTA.",
        "blocks": [
            ("page_hero", "Hero", "", {
                "eyebrow": "Services", "title": "Your Page Title",
                "description": "A short sub-headline about what you offer.",
                "image": "", "image_fill": True,
            }),
            ("feature_cards", "What we offer", "", {
                "heading": "What we offer", "sub": "", "columns": "3",
                "cards": [
                    {"title": "Service One", "subtitle": "", "accent": "#85addc", "image": "", "body": "Describe this service."},
                    {"title": "Service Two", "subtitle": "", "accent": "#f39ba2", "image": "", "body": "Describe this service."},
                    {"title": "Service Three", "subtitle": "", "accent": "#ac8cc0", "image": "", "body": "Describe this service."},
                ],
            }),
            ("pricing", "Pricing", "", {
                "heading": "Pricing", "sub": "",
                "plans": [
                    {"title": "Plan Name", "price": "₹0", "period": "/project", "features": "Feature one\nFeature two\nFeature three",
                     "cta_label": "Contact Us", "cta_url": "/contact-us", "highlighted": False},
                ],
            }),
            ("faq", "FAQ", "", {
                "heading": "Frequently asked questions",
                "items": [
                    {"q": "Sample question?", "a": "Sample answer — edit or remove this."},
                ],
            }),
            ("cta_banner", "Closing CTA", "", {
                "heading": "Ready to get started?", "sub": "",
                "bg_image": "", "primary_label": "Contact Us", "primary_url": "/contact-us",
                "secondary_label": "", "secondary_url": "",
            }),
        ],
    },

    "simple_content": {
        "label": "Simple Content Page",
        "description": "Just a hero and one content section — good for a policy or a short info page.",
        "blocks": [
            ("page_hero", "Hero", "", {
                "eyebrow": "", "title": "Your Page Title", "description": "",
                "image": "", "image_fill": True,
            }),
            ("content_section", "Content", "", {
                "eyebrow": "", "heading": "", "body": "<p>Write your content here.</p>",
                "image": "", "image_side": "none",
            }),
        ],
    },
}


def template_choices():
    return [(key, cfg["label"]) for key, cfg in PAGE_TEMPLATES.items()]
