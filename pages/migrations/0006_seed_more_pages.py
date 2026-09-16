"""Seed three more CMS-managed pages with their current live content:
Find a Dealer, Privacy Policy, Terms & Conditions.

Nothing on the public site changes yet: the front-end still renders its
hard-coded pages until each is wired to ``GET /api/pages/<slug>/`` (mirrors
migration 0003's approach for About Us / Contact Us / Rewards).

Deliberately NOT included here (see conversation record): Blog (already has
its own dedicated CMS), the design-variant home pages (/home1, /home2,
/home-apple), Brand Guide (a self-referential design-token reference page —
converting it would decouple it from the live tokens it exists to mirror),
and the catalog/category-driven pages (/products, /collection, /laminates,
/louvers, /asa-sheets, /surface-explorer, /applications and its subpages) —
these are backed by product data or disk-scanned manifests, not simple
editorial content, so they stay code-driven for now.
"""
from django.db import migrations


PRIVACY_SECTIONS = [
    ("1. Introduction", [
        "SAPPHIRE WOODS (INDIA) LLP, operating under the brand Sanish Laminates (\"Sanish\", \"we\", \"us\", or \"our\"), respects your privacy and is committed to protecting the personal information you share with us. This Privacy Policy explains how we collect, use, disclose and safeguard information when you visit our website, contact our team, register for our Rewards programme, or otherwise interact with us.",
        "By using our website or services, you agree to the collection and use of information in accordance with this policy. If you do not agree with the terms of this policy, please do not access or use our website.",
    ]),
    ("2. Information We Collect", [
        "We may collect personal information that you voluntarily provide to us, including your name, phone number, email address, company or business name, city/pincode, and any details you submit through our contact, dealer, or product enquiry forms.",
        "We may also collect non-personal information automatically as you browse our website, such as your IP address, browser type, device information, pages visited, and time spent on the site, through cookies and similar tracking technologies.",
        "If you register for the Sanish Rewards programme, we collect additional information necessary to process points, redemptions and payouts, such as your carpenter/professional details, UPI ID or bank account information for reward disbursal.",
    ]),
    ("3. How We Use Your Information", [
        "We use the information we collect to respond to your enquiries, process dealer and product requests, provide customer support, and administer the Rewards programme, including crediting points and processing redemptions.",
        "We may also use your information to send you updates about new collections, promotions, and offers, where you have opted in to receive such communications. You may unsubscribe from marketing communications at any time.",
        "We use aggregated, anonymised website usage data to understand how visitors interact with our site so that we can improve its content, layout and performance.",
    ]),
    ("4. Cookies & Tracking Technologies", [
        "Our website uses cookies and similar technologies to remember your preferences, understand site traffic, and improve your browsing experience. You can control or disable cookies through your browser settings; however, doing so may affect certain features of the website.",
    ]),
    ("5. Sharing of Information", [
        "We do not sell your personal information to third parties. We may share information with trusted service providers who assist us in operating our website, processing enquiries, or administering the Rewards programme (such as payment processors for reward disbursal), and who are contractually obligated to keep your information confidential.",
        "We may disclose information where required to comply with applicable law, regulation, legal process, or governmental request, or to protect the rights, property or safety of Sanish Laminates, our customers, or others.",
    ]),
    ("6. Data Security", [
        "We implement reasonable administrative, technical and physical safeguards designed to protect your personal information from unauthorised access, disclosure, alteration or destruction. However, no method of transmission over the internet or electronic storage is completely secure, and we cannot guarantee absolute security.",
    ]),
    ("7. Your Rights & Choices", [
        "You may request access to, correction of, or deletion of the personal information we hold about you by contacting us using the details below. We will respond to such requests in accordance with applicable law.",
        "You may opt out of receiving marketing communications from us at any time by using the unsubscribe link in our emails or by contacting us directly.",
    ]),
    ("8. Third-Party Links", [
        "Our website may contain links to third-party websites, including social media platforms and app stores. We are not responsible for the privacy practices or content of these third-party sites and encourage you to review their respective privacy policies.",
    ]),
    ("9. Children's Privacy", [
        "Our website and services are not directed at individuals under the age of 18, and we do not knowingly collect personal information from children. If we become aware that we have inadvertently collected such information, we will take steps to delete it.",
    ]),
    ("10. Changes to This Policy", [
        "We may update this Privacy Policy from time to time to reflect changes in our practices or for other operational, legal or regulatory reasons. The updated policy will be posted on this page with a revised \"Last updated\" date.",
    ]),
    ("11. Contact Us", [
        "If you have any questions or concerns about this Privacy Policy or how we handle your personal information, please contact us at info@sanishlaminate.com or (+91) 7027 777 032, or write to us at SAPPHIRE WOODS (INDIA) LLP, Regd. Office: 203 Aggarwal Chamber, Sainik Vihar, Pitam Pura, Delhi - 110034.",
    ]),
]

TERMS_SECTIONS = [
    ("1. Acceptance of Terms", [
        "These Terms & Conditions (\"Terms\") govern your access to and use of the website operated by SAPPHIRE WOODS (INDIA) LLP under the brand Sanish Laminates (\"Sanish\", \"we\", \"us\", or \"our\"). By accessing or using this website, you agree to be bound by these Terms. If you do not agree with any part of these Terms, please discontinue use of the website.",
    ]),
    ("2. Use of This Website", [
        "This website is intended to provide information about Sanish Laminates' products, collections, dealer network, and the Sanish Rewards programme. You agree to use this website only for lawful purposes and in a manner that does not infringe the rights of, restrict, or inhibit anyone else's use of the site.",
        "You must not misuse this website by knowingly introducing viruses, malware, or other technologically harmful material, or attempt to gain unauthorised access to any part of the website, the server on which it is hosted, or any connected system.",
    ]),
    ("3. Product Information & Availability", [
        "We make reasonable efforts to ensure that product descriptions, designs, finishes, dimensions and images displayed on this website are accurate. However, due to differences in display settings and manufacturing variances, actual product colour and texture may vary slightly from what is shown online. We recommend requesting a physical sample before finalising your order.",
        "Product availability, specifications and pricing are subject to change without prior notice. Inclusion of a product on this website does not guarantee its availability at all times or through all dealers.",
    ]),
    ("4. Intellectual Property", [
        "All content on this website, including but not limited to text, graphics, logos, product images, designs and the Sanish brand name and monogram, is the property of SAPPHIRE WOODS (INDIA) LLP or its licensors and is protected by applicable intellectual property laws.",
        "You may not reproduce, distribute, modify, publicly display, or create derivative works from any content on this website without our prior written consent, except for personal, non-commercial reference.",
    ]),
    ("5. Dealer & Distributor Network", [
        "Information regarding our dealer and distributor network is provided for convenience. Sanish Laminates is not responsible for the individual business practices, pricing, or conduct of independent dealers and distributors, and any transaction entered into with a dealer is solely between you and that dealer.",
    ]),
    ("6. Sanish Rewards Programme", [
        "Use of the Sanish Rewards mobile application and participation in the Rewards programme is subject to the programme's own terms, including eligibility, points accrual, redemption conditions and expiry rules, which are made available within the app. We reserve the right to modify, suspend or discontinue the Rewards programme at our discretion.",
    ]),
    ("7. Limitation of Liability", [
        "To the fullest extent permitted by applicable law, Sanish Laminates shall not be liable for any indirect, incidental, special or consequential damages arising out of or in connection with your use of this website or reliance on any information provided on it.",
        "Nothing in these Terms shall exclude or limit our liability for fraud, or for death or personal injury caused by our negligence, or any other liability that cannot be excluded or limited under applicable law.",
    ]),
    ("8. Warranty Disclaimer", [
        "This website and its content are provided on an \"as is\" and \"as available\" basis without warranties of any kind, either express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement. Product warranties, where applicable, are governed separately by the specific product warranty terms provided at the time of purchase.",
    ]),
    ("9. Governing Law & Jurisdiction", [
        "These Terms shall be governed by and construed in accordance with the laws of India. Any disputes arising out of or in connection with these Terms or your use of this website shall be subject to the exclusive jurisdiction of the courts at Delhi, India.",
    ]),
    ("10. Changes to These Terms", [
        "We may revise these Terms from time to time. The updated Terms will be posted on this page with a revised \"Last updated\" date, and your continued use of the website after such changes constitutes acceptance of the revised Terms.",
    ]),
    ("11. Contact Us", [
        "If you have any questions about these Terms & Conditions, please contact us at info@sanishlaminate.com or (+91) 7027 777 032, or write to us at SAPPHIRE WOODS (INDIA) LLP, Regd. Office: 203 Aggarwal Chamber, Sainik Vihar, Pitam Pura, Delhi - 110034.",
    ]),
]


def _legal_sections(sections):
    blocks = [
        ("content_section", "Last updated", "", {
            "eyebrow": "", "heading": "",
            "body": "<p>Last updated: July 2026</p>",
            "image": "", "image_side": "none",
        }),
    ]
    for heading, paragraphs in sections:
        body = "".join(f"<p>{p}</p>" for p in paragraphs)
        blocks.append(("content_section", heading, "", {
            "eyebrow": "", "heading": heading, "body": body,
            "image": "", "image_side": "none",
        }))
    return blocks


PAGES = [
    {"slug": "find-a-dealer", "title": "Find a Dealer", "path": "/find-a-dealer", "position": 4,
     "description": "Dealer network placeholder page with direct contact details.",
     "sections": [
        ("page_hero", "Hero", "", {
            "eyebrow": "Dealer Network",
            "title": "Find a Dealer",
            "description": "Connect with an authorised Sanish dealer for samples, product guidance and availability.",
            "image": "https://images.unsplash.com/photo-1528698827591-e19ccd7bc23d?q=80&w=2000",
            "image_fill": False,
        }),
        ("content_section", "Coming soon notice", "", {
            "eyebrow": "", "heading": "",
            "body": (
                "<p>Dealer network information coming soon.</p>"
                "<p>In the meantime, contact us directly: "
                "<a href=\"mailto:info@sanishlaminate.com\">info@sanishlaminate.com</a> or "
                "<a href=\"tel:+917027777032\">+91 7027 777 032</a>.</p>"
            ),
            "image": "", "image_side": "none",
        }),
     ]},

    {"slug": "privacy-policy", "title": "Privacy Policy", "path": "/privacy-policy", "position": 5,
     "description": "Legal — privacy policy.",
     "sections": [
        ("page_hero", "Hero", "", {
            "eyebrow": "Legal",
            "title": "Privacy Policy",
            "description": "How Sanish Laminates collects, uses and protects your information.",
            "image": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=2000",
            "image_fill": False,
        }),
        *_legal_sections(PRIVACY_SECTIONS),
     ]},

    {"slug": "terms-conditions", "title": "Terms & Conditions", "path": "/terms-conditions", "position": 6,
     "description": "Legal — terms and conditions.",
     "sections": [
        ("page_hero", "Hero", "", {
            "eyebrow": "Legal",
            "title": "Terms & Conditions",
            "description": "The terms governing your use of the Sanish Laminates website and services.",
            "image": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=2000",
            "image_fill": False,
        }),
        *_legal_sections(TERMS_SECTIONS),
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
        ("pages", "0005_alter_pagesection_block_type"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
