"""Seed CMS FormDefinitions for the forms that already exist in the site's
code (Contact Form, the site-wide Inquiry Popup, the Sample Request form).

Their fields mirror exactly what's hard-coded today, and ``target_pipeline``
is set to "inquiry" so submissions keep landing in ``leads.Inquiry`` / the
Leads dashboard exactly as before. This just makes their field sets
CMS-editable — nothing about where submissions go changes.

The Collection Inquiry Form (/collection) is deliberately not seeded here:
it maps its "purpose" selection to different Inquiry types (contact/dealer/
architect) client-side, which is a business-specific behavior best left as
code for now rather than force-fit into a single-field-set form.
"""
from django.db import migrations


FORMS = [
    {
        "slug": "contact-us-form",
        "name": "Contact Form",
        "description": "Powers the enquiry form on /contact-us.",
        "submit_label": "Submit Inquiry",
        "success_message": "Your inquiry has been received. Our team will get back to you within 24 hours.",
        "inquiry_type": "contact",
        "fields": [
            ("text", "name", "Name", "", True, []),
            ("tel", "phone", "Phone", "", True, []),
            ("email", "email", "Email", "", True, []),
            ("text", "pincode", "Pin Code", "", True, []),
            ("select", "enquire_type", "Enquire Type", "", True, ["Commercial", "Consumer"]),
            ("textarea", "message", "Message", "Enter the Product IDs You're Interested In", False, []),
        ],
    },
    {
        "slug": "inquiry-popup",
        "name": "Inquiry Popup",
        "description": "Powers the site-wide lead-capture popup (opens after 30s, or via catalogue downloads).",
        "submit_label": "Submit Inquiry",
        "success_message": "Thanks — we typically respond within 24 hours.",
        "inquiry_type": "contact",
        "fields": [
            ("text", "name", "Name", "", True, []),
            ("tel", "phone", "Phone", "", True, []),
            ("email", "email", "Email", "", True, []),
            ("text", "pincode", "Pin Code", "", True, []),
            ("select", "enquire_type", "Enquire Type", "", True, ["Commercial", "Consumer"]),
            ("textarea", "message", "Message", "Enter the Product IDs You're Interested In", False, []),
        ],
    },
    {
        "slug": "sample-request",
        "name": "Sample Request Form",
        "description": "Powers the \"Request Free Samples\" form on /home2.",
        "submit_label": "Request Samples",
        "success_message": "Thanks! Your sample request has been received.",
        "inquiry_type": "contact",
        "fields": [
            ("text", "name", "Name", "", True, []),
            ("tel", "phone", "Phone", "", True, []),
            ("email", "email", "Email", "", True, []),
            ("text", "pincode", "Pin Code", "", True, []),
            ("select", "enquire_type", "Enquire Type", "", True, ["Commercial", "Consumer"]),
        ],
    },
]


def seed(apps, schema_editor):
    FormDefinition = apps.get_model("formbuilder", "FormDefinition")
    FormField = apps.get_model("formbuilder", "FormField")

    for f in FORMS:
        form, created = FormDefinition.objects.get_or_create(
            slug=f["slug"],
            defaults={
                "name": f["name"],
                "description": f["description"],
                "submit_label": f["submit_label"],
                "success_message": f["success_message"],
                "target_pipeline": "inquiry",
                "inquiry_type": f["inquiry_type"],
                "is_system": True,
            },
        )
        if not created:
            continue
        for i, (field_type, name, label, placeholder, required, options) in enumerate(f["fields"]):
            FormField.objects.create(
                form=form, field_type=field_type, name=name, label=label,
                placeholder=placeholder, required=required, options=options, position=i,
            )


def unseed(apps, schema_editor):
    FormDefinition = apps.get_model("formbuilder", "FormDefinition")
    FormDefinition.objects.filter(slug__in=[f["slug"] for f in FORMS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("formbuilder", "0002_formdefinition_inquiry_type_and_more"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
