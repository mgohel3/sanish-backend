from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0013_show_thickness_default_off"),
    ]

    operations = [
        migrations.AddField(
            model_name="productattributeoption",
            name="swatch",
            field=models.CharField(blank=True, help_text="Colour dot shown in the website filter, e.g. #4A6FA5 (used by the Colour option).", max_length=9),
        ),
    ]
