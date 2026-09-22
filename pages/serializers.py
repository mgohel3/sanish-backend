from rest_framework import serializers
from .models import CityPage, PageTemplate, SitePage
from seo.schema_generators import generate_schema_json
from media_library.utils import absolutize_media_urls


class SitePageSerializer(serializers.ModelSerializer):
    """Public payload for ``GET /api/pages/<slug>/`` — enabled blocks, in order,
    each with its ``content`` merged over the block type's defaults."""

    sections = serializers.SerializerMethodField()

    def get_sections(self, obj):
        request = self.context.get("request")
        return [
            {
                "block_type": s.block_type,
                "anchor_id":  s.anchor_id,
                "content":    absolutize_media_urls(s.resolved(), request),
            }
            for s in obj.sections.filter(enabled=True)
        ]

    class Meta:
        model  = SitePage
        fields = ("slug", "title", "path", "sections")


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
        fields = ("id", "slug", "status", "resolved_data", "schema_json")
