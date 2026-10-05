import django.db.models.deletion
from django.db import migrations, models


def seed_categories(apps, schema_editor):
    Cat = apps.get_model("testimonials", "TestimonialCategory")
    T = apps.get_model("testimonials", "CarpenterTestimonial")
    carpenters, _ = Cat.objects.get_or_create(slug="carpenters", defaults={"name": "Carpenters", "position": 0})
    Cat.objects.get_or_create(slug="clients", defaults={"name": "Clients", "position": 1})
    T.objects.filter(category__isnull=True).update(category=carpenters)


class Migration(migrations.Migration):

    dependencies = [
        ("testimonials", "0002_seed_carpenters"),
    ]

    operations = [
        migrations.CreateModel(
            name="TestimonialCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=90, unique=True)),
                ("position", models.PositiveSmallIntegerField(default=0, help_text="Lower = appears first (tab order).")),
            ],
            options={
                "verbose_name": "Testimonial Category",
                "verbose_name_plural": "Testimonial Categories",
                "ordering": ["position", "id"],
            },
        ),
        migrations.AddField(
            model_name="carpentertestimonial",
            name="category",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="testimonials", to="testimonials.testimonialcategory",
            ),
        ),
        migrations.AlterModelOptions(
            name="carpentertestimonial",
            options={"ordering": ["position", "id"], "verbose_name": "Testimonial"},
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
