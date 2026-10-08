from django.db import migrations, models

SPACES = [
    "Kitchen", "Wardrobes", "Storage and Cabinets", "Living", "Bedroom",
    "Bathroom and Vanity", "Workspace", "Retail and Hospitality", "Close-ups",
]


def seed_and_backfill(apps, schema_editor):
    from django.utils.text import slugify
    Space = apps.get_model("gallery", "GallerySpace")
    Image = apps.get_model("gallery", "GalleryImage")
    Asset = apps.get_model("media_library", "MediaAsset")

    for pos, label in enumerate(SPACES):
        Space.objects.get_or_create(slug=slugify(label), defaults={"label": label, "position": pos})

    # Remember each photo's ORIGINAL filename (the CSV import matches on it). Legacy photos live at
    # /assets/img/gallery/<slug>/<name>.webp (name is the original); CMS uploads live in the Media
    # Library under a randomised stored name, so look the original up there.
    assets = {}
    for a in Asset.objects.all():
        for f in (a.file, a.webp_version):
            if f and f.name:
                assets[f.name] = a.original_filename
    for img in Image.objects.all():
        path = img.image or ""
        base = path.rsplit("/", 1)[-1]
        name = base
        if path.startswith("/media/"):
            rel = path[len("/media/"):]
            name = assets.get(rel) or base
        img.filename = name[:300]
        img.save(update_fields=["filename"])


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0002_seed_gallery"),
        ("media_library", "0002_alter_mediafolder_options_mediaasset_caption_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="GallerySpace",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("label", models.CharField(max_length=80, unique=True)),
                ("position", models.PositiveIntegerField(default=0)),
                ("enabled", models.BooleanField(default=True)),
            ],
            options={"ordering": ["position", "id"]},
        ),
        migrations.AddField(
            model_name="galleryimage",
            name="filename",
            field=models.CharField(blank=True, db_index=True, max_length=300,
                                   help_text="Original file name — the key the bulk tag CSV matches on."),
        ),
        migrations.AddField(
            model_name="galleryimage",
            name="sku",
            field=models.CharField(blank=True, max_length=60, help_text="SKU shown on the photo's detail page."),
        ),
        migrations.AddField(
            model_name="galleryimage",
            name="spaces",
            field=models.ManyToManyField(blank=True, related_name="images", to="gallery.galleryspace"),
        ),
        migrations.RunPython(seed_and_backfill, migrations.RunPython.noop),
    ]
