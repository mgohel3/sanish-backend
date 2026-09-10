"""Seed the CMS-managed pages with their current live content.

Nothing on the public site changes: the front-end still renders its hard-coded
pages until each one is wired to ``GET /api/pages/<slug>/``. This migration only
gives the CMS something real to edit.
"""
from django.db import migrations


PAGES = [
    {"slug": "home", "title": "Home Page", "path": "/", "position": 0,
     "description": "The public home page. Opens the block editor.",
     "external_url_name": "home_section_list", "sections": []},

    {"slug": "about-us", "title": "About Us", "path": "/about-us", "position": 1,
     "description": "Company story, mission & vision, certifications.",
     "sections": [
        ("page_hero", "Hero", "", {
            "eyebrow": "About Sanish Laminates",
            "title": "About Us",
            "description": "Innovation, precision and expressive surfaces for modern spaces.",
            "image": "/assets/img/about-page-banner.jpg",
            "image_fill": True,
        }),
        ("content_section", "Innovation and Design", "", {
            "eyebrow": "Best Laminate Company in India",
            "heading": "Innovation and Design",
            "body": (
                "<p>Founded in 2017, Sanish has made a strong foothold in the market as one of the "
                "fastest-growing laminate brands. With a strong commitment to innovation and design, "
                "we have stepped forward to bring the most innovative designs for your interior spaces.</p>"
                "<p>Our dedication goes beyond just products; it's about cultivating lasting connections. "
                "We prioritize delivering exceptional value to our clients, aiming to leave an indelible "
                "mark of quality, innovation, and beauty in every space we have the privilege to influence.</p>"
                "<p>At the heart of our success lies an unwavering commitment to research and development. "
                "Through extensive investment in R&amp;D, we bring forth products of the highest quality that "
                "are not only ahead of their time but also possess a timeless appeal in their design and craftsmanship.</p>"
            ),
            "image": "/assets/img/about/innovation-design.jpg",
            "image_side": "right",
        }),
        ("feature_cards", "Mission, Vision & Values", "values", {
            "heading": "Mission, Vision & Values",
            "sub": "",
            "columns": "3",
            "cards": [
                {"title": "Mission", "subtitle": "", "accent": "#85addc",
                 "image": "https://images.unsplash.com/photo-1517048676732-d65bc937f952?q=80&w=800",
                 "body": "Transforming spaces through the timeless design and longevity of our pioneering decorative solutions."},
                {"title": "Vision", "subtitle": "", "accent": "#f39ba2",
                 "image": "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=800",
                 "body": "To craft products that inspire people to adorn their spaces with unmatched aesthetic brilliance."},
                {"title": "Values", "subtitle": "", "accent": "#ac8cc0",
                 "image": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=800",
                 "body": "At Sanish, integrity is our cornerstone, guiding every interaction with unwavering honesty and transparency."},
            ],
        }),
        ("feature_cards", "Quality Certifications", "certifications", {
            "heading": "Quality Certifications",
            "sub": "Our manufacturing processes and products are independently certified to the highest national and international quality standards.",
            "columns": "2",
            "cards": [
                {"title": "ISO 9001:2015", "subtitle": "Quality Management System", "accent": "#85addc",
                 "image": "https://sanishlaminate.com/assets/images/certifications/certificateNo1.webp",
                 "body": "Certified by Otabu Certification Pvt. Ltd. as meeting the requirements of ISO 9001:2015 Quality Management System for manufacturers, traders, importers and exporters of HPL, laminates, plywood, block board and flush doors."},
                {"title": "Bureau of Indian Standards", "subtitle": "IS 2046 : 1995 Certified", "accent": "#fabf7d",
                 "image": "https://sanishlaminate.com/assets/images/certifications/certificateNo2_01.webp",
                 "body": "Licence No. CML-9100131599 issued by Bureau of Indian Standards (BIS) for Decorative Thermosetting Synthetic Resin Bonded Laminated Sheets, confirming compliance with Indian Standard IS 2046:1995."},
            ],
        }),
        ("cta_banner", "Closing CTA", "", {
            "heading": "Ready to elevate your space?",
            "sub": "Whether you're an architect working on a large-scale project or a homeowner looking for the perfect finish, our team is here to assist you with expert advice.",
            "bg_image": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?q=80&w=2000",
            "primary_label": "Contact Our Team", "primary_url": "/contact-us",
            "secondary_label": "Explore Collection", "secondary_url": "/collection",
        }),
     ]},

    {"slug": "contact-us", "title": "Contact Us", "path": "/contact-us", "position": 2,
     "description": "Headquarters details, map and the enquiry form.",
     "sections": [
        ("page_hero", "Hero", "", {
            "eyebrow": "Get in Touch",
            "title": "Contact Us",
            "description": "Speak with our team about products, samples, specifications and dealer support.",
            "image": "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=2000",
            "image_fill": True,
        }),
        ("contact_details", "Headquarters & form", "", {
            "heading": "Our Headquarters",
            "address": "SAPPHIRE WOODS (INDIA) LLP\nRegd. Office: 203 Aggarwal Chamber, Sainik Vihar\nPitam Pura, Delhi - 110034",
            "phones": [
                {"label": "(+91) 7027 777 032", "value": "+917027777032"},
                {"label": "(+91) 9876 543 210", "value": "+919876543210"},
            ],
            "emails": [
                {"value": "info@sanishlaminate.com"},
                {"value": "sales@sanishlaminate.com"},
            ],
            "map_embed_url": "https://maps.google.com/maps?q=Sanish+Laminate,28.6895846,77.1227317&z=17&ie=UTF8&iwloc=&output=embed",
            "form_heading": "Post your requirements",
            "form_sub": "Fill out the form below and our architectural consultants will get back to you within 24 hours.",
        }),
     ]},

    {"slug": "rewards", "title": "Rewards", "path": "/rewards", "position": 3,
     "description": "S'Rewards loyalty programme landing page.",
     "sections": [
        ("page_hero", "Hero", "", {
            "eyebrow": "S'Rewards Programme",
            "title": "Earn on every purchase",
            "description": "Join thousands of carpenters and contractors already earning with Sanish. Turn every purchase into points, gifts and cash rewards.",
            "image": "",
            "image_fill": True,
        }),
        ("feature_cards", "Programme perks", "perks", {
            "heading": "Why join S'Rewards",
            "sub": "",
            "columns": "4",
            "cards": [
                {"title": "Earn Points", "subtitle": "", "accent": "#85addc", "image": "/assets/img/icon/rewards-earn-points.svg",
                 "body": "Earn reward points on every purchase of Sanish products."},
                {"title": "Exclusive Offers", "subtitle": "", "accent": "#f39ba2", "image": "/assets/img/icon/rewards-exclusive-offers.svg",
                 "body": "Unlock member-only discounts, gifts, and seasonal promotions."},
                {"title": "Track Rewards", "subtitle": "", "accent": "#ac8cc0", "image": "/assets/img/icon/rewards-track-rewards.svg",
                 "body": "Real-time tracking of your points balance and redemption history."},
                {"title": "Easy Redemption", "subtitle": "", "accent": "#fabf7d", "image": "/assets/img/icon/rewards-easy-redemption.svg",
                 "body": "Redeem points instantly for cash discounts on your next order."},
            ],
        }),
        ("cta_banner", "Download CTA", "", {
            "heading": "Download the S'Rewards app",
            "sub": "Available on the App Store and Google Play.",
            "bg_image": "",
            "primary_label": "Learn more about the programme", "primary_url": "/rewards",
            "secondary_label": "", "secondary_url": "",
        }),
     ]},
]


def seed(apps, schema_editor):
    SitePage = apps.get_model("pages", "SitePage")
    PageSection = apps.get_model("pages", "PageSection")

    for pg in PAGES:
        page, _ = SitePage.objects.get_or_create(
            slug=pg["slug"],
            defaults={
                "title": pg["title"],
                "path": pg["path"],
                "position": pg["position"],
                "description": pg["description"],
                "external_url_name": pg.get("external_url_name", ""),
            },
        )
        if page.sections.exists():
            continue
        for i, (block_type, label, anchor, content) in enumerate(pg["sections"]):
            PageSection.objects.create(
                page=page, block_type=block_type, label=label,
                anchor_id=anchor, position=i, enabled=True, content=content,
            )


def unseed(apps, schema_editor):
    SitePage = apps.get_model("pages", "SitePage")
    SitePage.objects.filter(
        slug__in=[p["slug"] for p in PAGES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0002_sitepage_pagesection"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
