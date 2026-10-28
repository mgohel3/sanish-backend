from django.db import migrations, models

# The phone drawer used to be a hard-coded list; seed it as a system menu so it is editable in CMS > Menus.
ITEMS = [
        ('Home', '/', ''),
        ('Laminates', '/laminates', 'Decorative surfaces'),
        ('Louvers', '/louvers', 'Architectural panels'),
        ('Thermo Laminates', '/asa-sheets', 'Outdoor surfaces'),
        ('View All Products', '/products', 'Full product catalogue'),
        ('Collection', '/collection', 'All collections'),
        ('Applications', '/applications', ''),
        ('About Us', '/about-us', ''),
        ('Find a Dealer', '/find-a-dealer', 'Authorised dealers'),
        ('Contact Us', '/contact-us', ''),
]


def seed(apps, schema_editor):
    Menu = apps.get_model("menus", "Menu")
    MenuItem = apps.get_model("menus", "MenuItem")
    menu, created = Menu.objects.get_or_create(
        slug="mobile", defaults={"name": "Mobile Menu (phone drawer)", "is_system": True},
    )
    if created or not menu.items.exists():
        for pos, (label, url, sub) in enumerate(ITEMS):
            MenuItem.objects.create(menu=menu, label=label, url=url, subtitle=sub, position=pos)


def unseed(apps, schema_editor):
    apps.get_model("menus", "Menu").objects.filter(slug="mobile", is_system=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("menus", "0004_seed_system_menu_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="menuitem",
            name="subtitle",
            field=models.CharField(blank=True, default="", max_length=100, help_text="Optional small grey line under the label (used by the mobile menu)."),
        ),
        migrations.RunPython(seed, unseed),
    ]
