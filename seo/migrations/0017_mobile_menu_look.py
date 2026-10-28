from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("seo", "0016_mobile_menu")]

    operations = [
        migrations.AddField("sitesettings", "mobile_menu_effect", models.CharField(default="liquid", max_length=8)),
        migrations.AddField("sitesettings", "mobile_menu_overlay", models.CharField(default="60", max_length=3)),
        migrations.AddField("sitesettings", "mobile_menu_layout", models.CharField(default="list", max_length=6)),
        migrations.AddField("sitesettings", "mobile_menu_motion", models.CharField(default="normal", max_length=6)),
        migrations.AddField("sitesettings", "mobile_menu_show_social", models.BooleanField(default=True)),
    ]
