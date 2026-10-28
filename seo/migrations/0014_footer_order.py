from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo", "0013_footer_social"),
    ]

    operations = [
        migrations.AddField(model_name="sitesettings", name="footer_order",
            field=models.CharField(default="newsletter,apps,social", max_length=60, help_text='Order of the items under "Stay Connected" (comma-separated keys, set by drag and drop).')),
        migrations.AddField(model_name="sitesettings", name="footer_social_show_title",
            field=models.BooleanField(default=True, help_text="Show the heading above the social icons.")),
        migrations.AddField(model_name="sitesettings", name="footer_social_title",
            field=models.CharField(blank=True, default="Follow Us", max_length=60, help_text="Heading above the social icons.")),
        migrations.AddField(model_name="sitesettings", name="footer_social_title_font",
            field=models.CharField(blank=True, default="", max_length=10, help_text='"" = theme default, "serif" or "sans".')),
        migrations.AddField(model_name="sitesettings", name="footer_social_title_color",
            field=models.CharField(blank=True, default="", max_length=20, help_text="Hex colour for that heading; blank = theme default.")),
    ]
