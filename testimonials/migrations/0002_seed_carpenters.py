"""Seed the 5 real carpenters named in the 2026-10-01 request, with short
draft testimonials the Sanish team can edit any time from Dashboard >
Testimonials. These are placeholder copy, not quotes collected from the
carpenters themselves -- written to read naturally until real feedback
replaces them."""
from django.db import migrations

TESTIMONIALS = [
    {
        "name": "Nitesh Kumar",
        "role": "Professional Carpenter",
        "quote": "Sanish laminates give my work a premium finish every time, and the rewards make it even better.",
    },
    {
        "name": "Tasleem Ahmad",
        "role": "Professional Carpenter",
        "quote": "I've installed Sanish for two years now — consistent quality, and the app pays out fast.",
    },
    {
        "name": "Ravi Kumar",
        "role": "Professional Carpenter",
        "quote": "Easy to install, great finish, and real rewards for every sheet I scan.",
    },
    {
        "name": "Bhagwat Saran",
        "role": "Professional Carpenter",
        "quote": "From kitchens to wardrobes, Sanish never disappoints — and neither does the rewards app.",
    },
    {
        "name": "Baizad Ansari",
        "role": "Professional Carpenter",
        "quote": "Great material, fair rewards. Sanish respects the carpenters who build with it.",
    },
]


def seed(apps, schema_editor):
    CarpenterTestimonial = apps.get_model("testimonials", "CarpenterTestimonial")
    for i, t in enumerate(TESTIMONIALS):
        CarpenterTestimonial.objects.get_or_create(
            name=t["name"],
            defaults={"role": t["role"], "quote": t["quote"], "position": i, "is_active": True},
        )


def unseed(apps, schema_editor):
    CarpenterTestimonial = apps.get_model("testimonials", "CarpenterTestimonial")
    CarpenterTestimonial.objects.filter(name__in=[t["name"] for t in TESTIMONIALS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("testimonials", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(seed, unseed),
    ]
