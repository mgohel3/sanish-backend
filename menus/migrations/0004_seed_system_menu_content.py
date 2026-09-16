from django.db import migrations

# The content that is actually live on the site today (mirrored from the
# frontend's hardcoded fallbacks — see sanish-next-fixed/src/lib/navData.ts
# and sanish-next-fixed/src/components/Footer.tsx) — seeded here so the CMS
# reflects reality instead of showing empty system menus.
SEED_ITEMS = {
    "main": [
        ("Applications", "/applications"),
        ("About Us", "/about-us"),
    ],
    "topbar": [
        ("Dealer Network", "#"),
        ("Download Catalogue", "#"),
    ],
    "mega_quick": [
        ("Sustainability", "#"),
        ("Find a Dealer", "#"),
        ("Technical Support", "#"),
        ("Project Gallery", "#"),
    ],
    "footer_company": [
        ("About Us", "/about-us"),
        ("Applications", "/applications"),
        ("Blog", "/blog"),
        ("Rewards", "/rewards"),
        ("Contact Us", "/contact-us"),
    ],
}


def seed_content(apps, schema_editor):
    Menu = apps.get_model("menus", "Menu")
    MenuItem = apps.get_model("menus", "MenuItem")

    for slug, items in SEED_ITEMS.items():
        try:
            menu = Menu.objects.get(slug=slug)
        except Menu.DoesNotExist:
            continue
        if menu.items.exists():
            continue
        for position, (label, url) in enumerate(items):
            MenuItem.objects.create(menu=menu, label=label, url=url, position=position)


def unseed_content(apps, schema_editor):
    # No-op: don't delete content an admin may have since edited.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("menus", "0003_seed_system_menus"),
    ]

    operations = [
        migrations.RunPython(seed_content, unseed_content),
    ]
