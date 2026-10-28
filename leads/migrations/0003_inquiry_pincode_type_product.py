from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("leads", "0002_inquiry_form")]
    operations = [
        migrations.AddField(model_name="inquiry", name="pincode", field=models.CharField(blank=True, max_length=12)),
        migrations.AddField(model_name="inquiry", name="enquiry_type", field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name="inquiry", name="product", field=models.CharField(blank=True, max_length=200)),
    ]
