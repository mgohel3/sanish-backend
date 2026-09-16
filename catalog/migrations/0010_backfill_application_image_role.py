import os
import re

from django.db import migrations

# Same convention as the folder-import tool: a second image whose filename ends
# in "-preview" / "-applied" / "-pw" is the "applied in a room" shot rather than
# a plain gallery/swatch image.
_PREVIEW_SUFFIX_RE = re.compile(r"[-_ ](preview|applied|pw)$", re.I)


def backfill_application_role(apps, schema_editor):
    ProductImage = apps.get_model("catalog", "ProductImage")
    for pi in ProductImage.objects.select_related("asset").all():
        filename = getattr(pi.asset, "original_filename", "") or ""
        stem, _ext = os.path.splitext(filename)
        if _PREVIEW_SUFFIX_RE.search(stem):
            pi.role = "application"
            pi.save(update_fields=["role"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_product_application_image_url_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_application_role, noop),
    ]
