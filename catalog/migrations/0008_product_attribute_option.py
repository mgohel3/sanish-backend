from django.db import migrations, models


def seed_options(apps, schema_editor):
    ProductAttributeOption = apps.get_model("catalog", "ProductAttributeOption")
    Product = apps.get_model("catalog", "Product")

    design_types = ["Wood", "Stone", "Fabric", "Solid", "Metallic"]
    colors = [
        "White", "Beige", "Black", "Blue", "Brown", "Green", "Grey",
        "Metallic", "Multicolor", "Orange", "Pink", "Purple", "Red", "Yellow",
    ]
    badges = ["New", "Bestseller", "Limited"]

    for attribute, values in (
        ("design_type", design_types),
        ("color", colors),
        ("badge", badges),
    ):
        for pos, value in enumerate(values):
            ProductAttributeOption.objects.get_or_create(
                attribute=attribute, value=value, defaults={"position": pos}
            )

    # Finish had no fixed choice list — seed it from whatever values already
    # exist on products today, plus a few sensible defaults.
    existing_finishes = (
        Product.objects.exclude(finish="")
        .values_list("finish", flat=True)
        .distinct()
    )
    finishes = sorted({f.strip() for f in existing_finishes if f.strip()})
    for extra in ["High Gloss", "Matte", "Suede", "Textured"]:
        if extra not in finishes:
            finishes.append(extra)
    for pos, value in enumerate(finishes):
        ProductAttributeOption.objects.get_or_create(
            attribute="finish", value=value, defaults={"position": pos}
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0007_product_show_application_product_show_design_type_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductAttributeOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attribute", models.CharField(choices=[
                    ("design_type", "Design Type"),
                    ("color", "Colour"),
                    ("badge", "Badge"),
                    ("finish", "Finish"),
                ], max_length=20)),
                ("value", models.CharField(max_length=60)),
                ("position", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ["attribute", "position", "id"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="productattributeoption",
            unique_together={("attribute", "value")},
        ),
        migrations.RunPython(seed_options, noop),
    ]
