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


class BlogAuthorSerializer(serializers.Serializer):
    """Lightweight public author card for the article sidebar."""
    id     = serializers.IntegerField()
    name   = serializers.SerializerMethodField()
    role   = serializers.CharField(source="get_role_display", default="")
    avatar = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_avatar(self, obj):
        av = getattr(obj, "avatar", None)
        return av.url if av else None


class _ImageMixin(serializers.Serializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.featured_image_url:
            return obj.featured_image_url
        if obj.featured_image_id and obj.featured_image:
            return obj.featured_image.url
        return None


class BlogPostListSerializer(_ImageMixin, serializers.ModelSerializer):
    featured_image = MediaAssetSerializer(read_only=True)
    categories     = BlogCategorySerializer(many=True, read_only=True)

    class Meta:
        model  = BlogPost
        fields = (
            "id", "title", "slug", "excerpt", "image", "featured_image",
            "categories", "status", "published_at", "created",
        )


class BlogPostDetailSerializer(_ImageMixin, serializers.ModelSerializer):
    featured_image = MediaAssetSerializer(read_only=True)
    categories     = BlogCategorySerializer(many=True, read_only=True)
    tags           = TagSerializer(many=True, read_only=True)
    author         = BlogAuthorSerializer(read_only=True)

    class Meta:
        model  = BlogPost
        fields = (
            "id", "title", "slug", "excerpt", "layout", "image", "featured_image", "content",
            "categories", "tags", "author",
            "show_author", "show_share", "show_related",
            "seo_title", "meta_description", "meta_keywords",
            "status", "published_at", "created", "updated",
            "faqs", "auto_faq_schema",
        )
