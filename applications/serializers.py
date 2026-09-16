from rest_framework import serializers

from .models import ApplicationCategory, ApplicationProject


class ApplicationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationCategory
        fields = ("slug", "label", "description", "accent", "image", "gallery")


class ApplicationProjectListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.label", read_only=True)

    class Meta:
        model = ApplicationProject
        fields = ("slug", "label", "category", "finish", "image", "tall")


class ApplicationProjectDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.label", read_only=True)

    class Meta:
        model = ApplicationProject
        fields = (
            "slug", "label", "category", "finish", "image", "tall",
            "description", "location", "year", "designer", "area",
            "gallery", "highlights", "products",
        )
