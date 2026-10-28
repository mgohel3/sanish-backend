from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("menus", "0005_mobile_menu")]

    operations = [
        migrations.AddField("menuitem", "badge", models.CharField(blank=True, default="", max_length=20)),
        migrations.AddField("menuitem", "icon", models.CharField(blank=True, default="", max_length=20)),
    ]
