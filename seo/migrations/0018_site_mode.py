from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("seo", "0017_mobile_menu_look")]

    operations = [
        migrations.AddField("sitesettings", "site_mode", models.CharField(default="off", max_length=12)),
        migrations.AddField("sitesettings", "site_mode_launch_at", models.CharField(blank=True, default="", max_length=16)),
        migrations.AddField("sitesettings", "site_mode_title", models.CharField(blank=True, default="", max_length=200)),
        migrations.AddField("sitesettings", "site_mode_message", models.TextField(blank=True, default="")),
        migrations.AddField("sitesettings", "site_mode_show_timer", models.BooleanField(default=True)),
        migrations.AddField("sitesettings", "site_mode_auto_open", models.BooleanField(default=True)),
        migrations.AddField("sitesettings", "site_mode_bypass_key", models.CharField(default="sanish-preview", max_length=40)),
    ]
