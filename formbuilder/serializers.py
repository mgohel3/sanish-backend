from rest_framework import serializers

from seo.recaptcha import verify_recaptcha
from .models import FormDefinition, FormField, FormSubmission


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ("name", "field_type", "label", "placeholder", "help_text", "required", "options")


class FormDefinitionSerializer(serializers.ModelSerializer):
    """Public payload for ``GET /api/forms/<slug>/`` — the field schema a
    frontend needs to render the form."""

    fields = FormFieldSerializer(many=True, read_only=True)

    class Meta:
        model = FormDefinition
        fields = ("slug", "name", "description", "submit_label", "success_message", "fields")


class FormSubmissionCreateSerializer(serializers.ModelSerializer):
    """Validates a submission's ``data`` against the target form's field
    definitions (required fields present) before saving."""

    slug = serializers.SlugField(write_only=True)
    recaptcha_token = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = FormSubmission
        fields = ("slug", "data", "source_page", "recaptcha_token")

    def validate(self, attrs):
        slug = attrs.pop("slug")
        token = attrs.pop("recaptcha_token", "")
        try:
            form = FormDefinition.objects.prefetch_related("fields").get(slug=slug)
        except FormDefinition.DoesNotExist:
            raise serializers.ValidationError({"slug": "Unknown form."})

        data = attrs.get("data") or {}
        if not isinstance(data, dict):
            raise serializers.ValidationError({"data": "Must be an object of field name -> value."})

        errors = {}
        for field in form.fields.all():
            value = data.get(field.name)
            if field.required and (value is None or value == ""):
                errors[field.name] = "This field is required."
        if errors:
            raise serializers.ValidationError(errors)

        request = self.context.get("request")
        remote_ip = request.META.get("REMOTE_ADDR") if request else None
        ok, error = verify_recaptcha(token, remote_ip)
        if not ok:
            raise serializers.ValidationError({"recaptcha_token": error})

        attrs["form"] = form
        return attrs
