from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo", "0012_footer_toggles"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="footer_show_social",
            field=models.BooleanField(default=True, help_text='Show the social media icons under "Stay Connected" in the footer.'),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="footer_social_icon_size",
            field=models.PositiveSmallIntegerField(default=38, help_text="Footer social icon button size in pixels (24-72)."),
        ),
    ]
