from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo", "0010_pageseo"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="designs_count",
            field=models.CharField(blank=True, default="800+", help_text='Number of designs shown on the website, e.g. "800+" (home hero, header menu).', max_length=20),
        ),
    ]
