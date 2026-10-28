from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo", "0015_site_sound"),
    ]

    operations = [
        migrations.AddField(model_name="sitesettings", name="mobile_menu_style",
            field=models.CharField(default="drawer_right", max_length=14, help_text="drawer_right, drawer_left or fullscreen.")),
        migrations.AddField(model_name="sitesettings", name="mobile_menu_theme",
            field=models.CharField(default="light", max_length=6, help_text="light, dark or brand.")),
        migrations.AddField(model_name="sitesettings", name="mobile_menu_bg_color",
            field=models.CharField(blank=True, default="", max_length=20, help_text="Optional hex background colour; overrides the theme background.")),
        migrations.AddField(model_name="sitesettings", name="mobile_menu_bg_image",
            field=models.CharField(blank=True, default="", max_length=500, help_text="Optional background image path or URL.")),
        migrations.AddField(model_name="sitesettings", name="mobile_menu_logo_url",
            field=models.CharField(blank=True, default="", max_length=500, help_text="Logo shown at the top of the mobile menu; blank = the brand mark.")),
        migrations.AddField(model_name="sitesettings", name="mobile_menu_show_catalogue",
            field=models.BooleanField(default=True, help_text="Show the Download Catalogue button in the mobile menu.")),
        migrations.AddField(model_name="sitesettings", name="mobile_menu_show_contact",
            field=models.BooleanField(default=True, help_text="Show the Call Us / Email Us buttons in the mobile menu.")),
    ]
