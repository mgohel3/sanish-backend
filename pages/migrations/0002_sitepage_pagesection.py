import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SitePage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(help_text='Matches the CMS/API key, e.g. "about-us".', max_length=80, unique=True)),
                ("title", models.CharField(max_length=120)),
                ("path", models.CharField(blank=True, help_text='Front-end route for the "Preview" link, e.g. "/about-us".', max_length=120)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("position", models.PositiveIntegerField(default=0)),
                ("is_system", models.BooleanField(default=True, help_text="System pages cannot be deleted from the CMS.")),
                ("external_url_name", models.CharField(blank=True, max_length=80)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Site Page", "ordering": ["position", "id"]},
        ),
        migrations.CreateModel(
            name="PageSection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("block_type", models.CharField(max_length=40)),
                ("label", models.CharField(help_text="Internal name shown in the CMS list (not published).", max_length=120)),
                ("anchor_id", models.SlugField(blank=True, help_text='Optional id for the <section> tag (e.g. "team" -> /about-us#team).', max_length=60)),
                ("position", models.PositiveIntegerField(default=0)),
                ("enabled", models.BooleanField(default=True)),
                ("content", models.JSONField(blank=True, default=dict)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("page", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sections", to="pages.sitepage")),
            ],
            options={"verbose_name": "Page Section", "ordering": ["position", "id"]},
        ),
    ]
