from django.db import migrations

# Mirrors seo.NavLink.GROUP_CHOICES — kept as plain tuples here so this
# migration stays valid even if that model changes later.
GROUPS = [
    ("main", "Main Navigation (desktop nav bar)"),
    ("topbar", "Top Bar (above the header)"),
    ("mega_quick", "Mega Menu — Bottom Quick Links"),
    ("footer_company", "Footer — Company column"),
]


def seed_system_menus(apps, schema_editor):
    Menu = apps.get_model("menus", "Menu")
    MenuItem = apps.get_model("menus", "MenuItem")
    NavLink = apps.get_model("seo", "NavLink")

    menus_by_group = {}
    for slug, name in GROUPS:
        menu, _ = Menu.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "is_system": True},
        )
        menus_by_group[slug] = menu

    for link in NavLink.objects.all():
        menu = menus_by_group.get(link.group)
        if menu is None:
            continue
        MenuItem.objects.create(
            menu=menu,
            label=link.label,
            url=link.url,
            open_new_tab=link.open_new_tab,
            position=link.position,
            active=link.active,
        )


def unseed_system_menus(apps, schema_editor):
    Menu = apps.get_model("menus", "Menu")
    Menu.objects.filter(slug__in=[g[0] for g in GROUPS], is_system=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("menus", "0002_menuitem_active"),
        ("seo", "0003_nav_link"),
    ]

    operations = [
        migrations.RunPython(seed_system_menus, unseed_system_menus),
    ]
