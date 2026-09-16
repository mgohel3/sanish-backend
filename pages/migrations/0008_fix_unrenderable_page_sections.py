# Data fix: the CMS "Add block" picker used to offer every homepage-only
# block type (about, hero, …) on generic pages too, but the frontend's
# generic-page renderer only knows the INNER_PAGE_BLOCKS set — anything else
# silently rendered as nothing. Convert any such stray sections on non-home
# pages to the closest generic equivalent ("content_section") so their
# content is visible again.
from django.db import migrations

INNER_PAGE_BLOCKS = {
    "page_hero", "content_section", "feature_cards", "faq", "contact_details",
    "rich_text", "image_text", "cta_banner", "testimonials", "gallery",
    "team", "pricing", "stats", "logos_strip", "video_embed",
}


def fix_sections(apps, schema_editor):
    SitePage = apps.get_model("pages", "SitePage")
    for page in SitePage.objects.filter(external_url_name=""):
        for section in page.sections.all():
            if section.block_type in INNER_PAGE_BLOCKS:
                continue
            content = section.content or {}
            section.block_type = "content_section"
            section.content = {
                "eyebrow": "",
                "heading": content.get("heading", ""),
                "body": content.get("body", "") or content.get("description", ""),
                "image": content.get("image", "") or content.get("bg_image", ""),
                "image_side": "right",
            }
            section.save(update_fields=["block_type", "content"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_add_sitepage_is_published'),
    ]

    operations = [
        migrations.RunPython(fix_sections, noop),
    ]
