from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("seo", "0018_site_mode")]
    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="applications_mobile_layout",
            field=models.CharField(default="grid2", max_length=10),
        ),
    ]
