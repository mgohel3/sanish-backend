from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo", "0014_footer_order"),
    ]

    operations = [
        migrations.AddField(model_name="sitesettings", name="sound_enabled",
            field=models.BooleanField(default=False, help_text="Play a background sound on the website (starts after the visitor's first click or tap).")),
        migrations.AddField(model_name="sitesettings", name="sound_url",
            field=models.CharField(blank=True, default="", max_length=500, help_text="Audio file path or URL (MP3 recommended), e.g. from the Media Library.")),
        migrations.AddField(model_name="sitesettings", name="sound_show_button",
            field=models.BooleanField(default=True, help_text="Show the floating Sound On/Off button.")),
        migrations.AddField(model_name="sitesettings", name="sound_button_size",
            field=models.PositiveSmallIntegerField(default=40, help_text="Height of the Sound button in pixels (28-72).")),
        migrations.AddField(model_name="sitesettings", name="sound_volume",
            field=models.PositiveSmallIntegerField(default=35, help_text="Volume 0-100.")),
        migrations.AddField(model_name="sitesettings", name="sound_position",
            field=models.CharField(default="left", max_length=5, help_text="Which bottom corner the Sound button sits in: left or right.")),
    ]
