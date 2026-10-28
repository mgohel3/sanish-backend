from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo", "0009_alter_sitesettings_header_cta_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageSEO",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("path", models.CharField(help_text='Page address, e.g. "/" or "/laminates"', max_length=300, unique=True)),
                ("label", models.CharField(help_text="Name shown in the CMS", max_length=120)),
                ("meta_title", models.CharField(blank=True, help_text="Browser tab / Google title. Aim for 50-60 characters.", max_length=200)),
                ("meta_description", models.CharField(blank=True, help_text="Google snippet. Aim for 150-160 characters.", max_length=400)),
                ("og_image", models.CharField(blank=True, help_text="Image shown when the page is shared (WhatsApp, LinkedIn...). 1200x630 works best.", max_length=500)),
                ("noindex", models.BooleanField(default=False, help_text="Ask Google not to list this page.")),
                ("position", models.PositiveIntegerField(default=0)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Page SEO", "verbose_name_plural": "Page SEO", "ordering": ["position", "path"]},
        ),
    ]
