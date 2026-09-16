import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_library', '0001_initial'),
        ('catalog', '0010_backfill_application_image_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='pdf_catalog',
            field=models.ForeignKey(blank=True, help_text="Catalogue PDF for this collection, shown as a download on its product listing pages.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='collection_pdfs', to='media_library.mediaasset'),
        ),
    ]
