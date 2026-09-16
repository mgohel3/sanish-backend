"""Seed the site FAQ list from the FAQs already written into blog posts.

Two sources, both already-published content — nothing invented here:
1. ``BlogPost.faqs`` — the structured FAQ repeater field, present on 9 posts.
2. One post ("creative-ways-to-use-HPL-sheets") that has an FAQ section
   written directly into its HTML body (``<h4>Q…</h4><p>answer</p>``) instead
   of the structured field — extracted with the same regex used to verify it.

No duplicate questions were found across posts, so every FAQ found is kept.
"""
import re

from django.db import migrations

CONTENT_FAQ_SLUGS = ["creative-ways-to-use-HPL-sheets"]

_QA_RE = re.compile(r"<h4>\s*Q\d*:?\s*(.*?)</h4>\s*(.*?)(?=<h[234]>|$)", re.S | re.I)
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_tags(html):
    return re.sub(r"\s+", " ", _TAG_RE.sub("", html)).strip()


def _extract_from_content(html):
    pairs = []
    for m in _QA_RE.finditer(html or ""):
        question = _strip_tags(m.group(1))
        answer = _strip_tags(m.group(2))
        if question and answer:
            pairs.append((question, answer))
    return pairs


def import_faqs(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")
    Faq = apps.get_model("faq", "Faq")

    position = 0

    for post in BlogPost.objects.exclude(faqs=[]).order_by("id"):
        for item in (post.faqs or []):
            question = (item.get("question") or "").strip()
            answer = (item.get("answer") or "").strip()
            if not question or not answer:
                continue
            Faq.objects.create(
                question=question, answer=answer,
                source_post=post, position=position, is_active=True,
            )
            position += 1

    for slug in CONTENT_FAQ_SLUGS:
        post = BlogPost.objects.filter(slug=slug).first()
        if not post:
            continue
        for question, answer in _extract_from_content(post.content):
            Faq.objects.create(
                question=question, answer=answer,
                source_post=post, position=position, is_active=True,
            )
            position += 1


def remove_imported_faqs(apps, schema_editor):
    Faq = apps.get_model("faq", "Faq")
    Faq.objects.filter(source_post__isnull=False).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("faq", "0001_initial"),
        ("blog", "0005_blogpost_excerpt"),
    ]

    operations = [
        migrations.RunPython(import_faqs, remove_imported_faqs),
    ]
