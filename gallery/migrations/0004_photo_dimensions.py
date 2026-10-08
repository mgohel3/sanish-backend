from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0003_spaces_and_photo_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="galleryimage",
            name="width",
            field=models.PositiveIntegerField(blank=True, null=True, help_text="Pixel size \u2014 lets the collage reserve space before the photo loads."),
        ),
        migrations.AddField(
            model_name="galleryimage",
            name="height",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
