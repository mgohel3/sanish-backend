from rest_framework import serializers
from .models import BlogPost, BlogCategory, Tag
from catalog.serializers import MediaAssetSerializer


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = BlogCategory
        fields = ("id", "name", "slug")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ("id", "name", "slug")


class BlogPostListSerializer(serializers.ModelSerializer):
    featured_image = MediaAssetSerializer(read_only=True)
    categories     = BlogCategorySerializer(many=True, read_only=True)

    class Meta:
        model  = BlogPost
        fields = ("id", "title", "slug", "featured_image", "categories", "status", "published_at", "created")


class BlogPostDetailSerializer(serializers.ModelSerializer):
    featured_image = MediaAssetSerializer(read_only=True)
    categories     = BlogCategorySerializer(many=True, read_only=True)
    tags           = TagSerializer(many=True, read_only=True)

    class Meta:
        model  = BlogPost
        fields = (
            "id", "title", "slug", "featured_image", "content",
            "categories", "tags",
            "seo_title", "meta_description", "meta_keywords",
            "status", "published_at", "created", "updated",
        )
