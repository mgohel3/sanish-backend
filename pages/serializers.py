from rest_framework import serializers
from .models import CityPage, PageTemplate
from seo.schema_generators import generate_schema_json


class CityPageListSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CityPage
        fields = ("slug", "city", "state", "status")


class CityPageDetailSerializer(serializers.ModelSerializer):
    resolved_data = serializers.SerializerMethodField()
    schema_json   = serializers.SerializerMethodField()

    def get_resolved_data(self, obj):
        return obj.resolved()

    def get_schema_json(self, obj):
        resolved = obj.resolved()
        return generate_schema_json(
            schema_type=resolved.get("schema_type", "LocalBusiness"),
            city=obj.city,
            state=obj.state,
            product=obj.template.product_type_label,
            faqs=resolved.get("faqs", []),
            page_url=resolved["seo"].get("canonical_url", ""),
            title=resolved.get("h1_title", ""),
        )

    class Meta:
        model  = CityPage
        fields = ("slug", "resolved_data", "schema_json")
