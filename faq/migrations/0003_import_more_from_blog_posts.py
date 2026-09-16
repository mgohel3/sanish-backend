"""Curated additional FAQs gathered from the remaining blog posts' section
headings (question-style h2/h3/h4 followed by an answer paragraph) — not
just the structured BlogPost.faqs field this time. Hand-curated allowlist:
CTA/marketing headings ("Ready to...", "Why Choose Sanish...") and near-
duplicate questions (same definition asked near-identically across two or
more posts, or the same post twice) were excluded so nothing repetitive
ships. Answers are re-extracted from the live post content at migration
time (matched by slug + exact question text) rather than retyped here, so
the source of truth stays the blog post itself."""
import re

from django.db import migrations

ALLOWLIST = [
    ('achieve-wood-luxury-look-using-veneer-finish-laminates', 'Why Choose Laminates with a Veneer Finish?'),
    ('affordable-yet-stylish-wood-laminate-sheets-for-cabinets', 'What Are Wood Laminate Sheets?'),
    ('anti-fingerprint-laminates-for-kitchens', 'What is Anti-Fingerprint Laminate?'),
    ('best-laminate-for-kitchen-cabinets', 'What type of laminate is best for kitchen cabinets?'),
    ('best-laminates-for-small-kitchens', 'Why Are Laminates the Best Choice for Small Kitchens?'),
    ('budget-friendly-kitchen-makeover', 'What Makes Laminate Kitchen Cabinets the Best Option?'),
    ('buy-best-laminate-online', 'What Qualities Make a Laminate "The Best"?'),
    ('decorative-laminated-plywood-sheets', 'What Are Decorative Laminated Plywood Sheets?'),
    ('decorative-laminated-plywood-sheets', 'Why Use Decorative Laminated Plywood Sheets for Your Home?'),
    ('decorative-laminates-in-india', 'Comparing Glossy vs. Matte Decorative Laminates: What Works Best for Indian Interiors?'),
    ('flexible-laminate-veneer-vs-traditional-materials', 'What is Flexible Laminate Veneer?'),
    ('flexible-laminate-veneer-vs-traditional-materials', 'What’s Best for Your Kitchen Cabinets?'),
    ('flexible-laminate-veneers-for-your-kitchen-cabinets', 'Why Choose Flexible Laminate Veneers for Your Kitchen Cabinets?'),
    ('flexible-laminate-veneers-vs-traditional-veneers', 'Flexible Laminate Veneers vs. Traditional Veneers: Which is Best for Kitchen Cabinets?'),
    ('glossy-laminates-for-bedroom-wardrobes', 'What Are Glossy Laminates For Wardrobes?'),
    ('glossy-laminates-for-kitchen', 'Why the gloss?'),
    ('glossy-laminates-for-kitchen', 'But style isn’t everything, right?'),
    ('glossy-laminates-for-kitchen', 'What about long-term durability?'),
    ('high-gloss-laminate-sheets-for-wardrobe', 'High Gloss Laminate Sheets: What Are They?'),
    ('high-gloss-laminate-sheets-for-wardrobe', 'Why Pick Wardrobe High Gloss Laminates?'),
    ('high-gloss-laminates-easy-to-clean', 'Why Should Your Kitchen Have High-Gloss Laminates?'),
    ('high-gloss-vs-acrylic', 'Which Is Better to Pick?'),
    ('high-pressure-laminate-sheets', 'Why Select High-Pressure Laminate Sheets Over Other Laminates?'),
    ('high-pressure-laminates-vs-low-pressure-laminates', 'What is High-Pressure Laminate (HPL)?'),
    ('high-pressure-laminates-vs-low-pressure-laminates', 'What is Low-Pressure Laminate (LPL)?'),
    ('is-laminate-good-for-kitchen-cabinets', 'Is laminate good for kitchen cabinets?'),
    ('laminate-for-wardrobe-door', 'Why Choose Laminates for Wardrobe Doors?'),
    ('laminates-for-wardrobe', 'Is Laminate the Right Choice for Your Wardrobe?'),
    ('lamination-for-wardrobe', 'Why Choose Lamination for Wardrobes?'),
    ('modern-charm-of-high-gloss-laminates', 'How Are They Made?'),
    ('modern-two-colour-combination-for-kitchen-laminates', 'Why Two-Tone?'),
    ('modular-vs-custom-laminate-kitchen-cabinets', 'Modular vs. Custom Laminate Kitchen Cabinets: What to Choose?'),
    ('modular-vs-custom-laminate-kitchen-cabinets', 'What makes laminate cabinets so popular?'),
    ('modular-vs-custom-laminate-kitchen-cabinets', 'What Laminate Finish Works Best?'),
    ('sheet-laminate-for-cabinets', 'Why Choose Sheet Laminates for Cabinets?'),
    ('veneer-finish-laminates', 'What Are Veneer Finish Laminates?'),
    ('waterproof-high-gloss-laminates', 'Are High Gloss Laminates Waterproof?'),
    ('waterproof-laminates', 'What Are Waterproof Laminates?'),
    ('wood-laminate-sheets', 'Love the wood look but not the upkeep?'),
    ('wood-laminate-sheets', 'Worried about daily wear and tear?'),
    ('wood-laminate-sheets', "Wondering if they're eco-friendly?"),
    ('wood-laminate-sheets', 'Need something that matches your vibe?'),
    ('wood-laminate-sheets', 'What about cleaning and maintenance?'),
]

_HEAD_RE = re.compile(r"<(h[234])[^>]*>\s*(.*?)\s*</h[234]>", re.I | re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_tags(html):
    return re.sub(r"\s+", " ", _TAG_RE.sub("", html or "")).strip()


def _extract_qas(content):
    heads = list(_HEAD_RE.finditer(content or ""))
    pairs = []
    for i, m in enumerate(heads):
        question = _strip_tags(m.group(2))
        if not question.endswith("?"):
            continue
        start = m.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(content)
        answer = _strip_tags(content[start:end])
        if answer:
            pairs.append((question, answer))
    return pairs


def import_more_faqs(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")
    Faq = apps.get_model("faq", "Faq")

    by_slug = {}
    for slug, question in ALLOWLIST:
        by_slug.setdefault(slug, set()).add(question)

    last = Faq.objects.order_by("-position").first()
    position = (last.position + 1) if last else 0

    for slug, wanted_questions in by_slug.items():
        post = BlogPost.objects.filter(slug=slug).first()
        if not post:
            continue
        for question, answer in _extract_qas(post.content):
            if question not in wanted_questions:
                continue
            Faq.objects.create(
                question=question, answer=answer,
                source_post=post, position=position, is_active=True,
            )
            position += 1


def remove_more_faqs(apps, schema_editor):
    Faq = apps.get_model("faq", "Faq")
    questions = {q for _, q in ALLOWLIST}
    Faq.objects.filter(question__in=questions).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("faq", "0002_import_from_blog_posts"),
    ]

    operations = [
        migrations.RunPython(import_more_faqs, remove_more_faqs),
    ]
