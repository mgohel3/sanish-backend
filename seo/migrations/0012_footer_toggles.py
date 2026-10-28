from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo", "0011_sitesettings_designs_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="footer_show_newsletter",
            field=models.BooleanField(default=True, help_text='Show the "Stay Connected" email subscribe box in the footer.'),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="footer_show_apps",
            field=models.BooleanField(default=True, help_text="Show the Google Play / App Store buttons in the footer."),
        ),
    ]
