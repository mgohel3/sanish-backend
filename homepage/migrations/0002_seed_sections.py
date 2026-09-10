from django.db import migrations

from homepage.blocks import SEED_ORDER


def seed(apps, schema_editor):
    HomeSection = apps.get_model("homepage", "HomeSection")
    for position, (block_type, label, enabled) in enumerate(SEED_ORDER):
        HomeSection.objects.get_or_create(
            block_type=block_type,
            defaults={
                "label": label,
                "position": position,
                "enabled": enabled,
                "content": {},
            },
        )


def unseed(apps, schema_editor):
    HomeSection = apps.get_model("homepage", "HomeSection")
    HomeSection.objects.filter(
        block_type__in=[bt for bt, _, _ in SEED_ORDER]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("homepage", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
