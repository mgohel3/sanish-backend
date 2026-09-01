from rest_framework import serializers
from .models import Category, Collection, Product, ProductImage
from media_library.models import MediaAsset


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return obj.url

    class Meta:
        model  = MediaAsset
        fields = ("id", "url", "original_url", "alt_text", "title", "width", "height", "type")


class CategorySerializer(serializers.ModelSerializer):
    banner_image = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = Category
        fields = (
            "id", "name", "slug", "description", "banner_image",
            "mega_group", "mega_icon", "mega_description", "mega_position",
            "seo_title", "meta_description", "meta_keywords", "status",
        )


class CollectionSerializer(serializers.ModelSerializer):
    images = MediaAssetSerializer(many=True, read_only=True)

    class Meta:
        model  = Collection
        fields = (
            "id", "name", "slug", "description", "images",
            "show_in_mega_menu", "mega_accent_color", "mega_position",
            "seo_title", "meta_description", "meta_keywords", "status",
        )


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = MediaAssetSerializer(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model  = Product
        fields = ("id", "name", "sku", "slug", "category_name", "primary_image", "status")


class ProductDetailSerializer(serializers.ModelSerializer):
    images    = serializers.SerializerMethodField()
    category  = CategorySerializer(read_only=True)
    collection = CollectionSerializer(read_only=True)
    pdf_catalog = MediaAssetSerializer(read_only=True)
    related_products = ProductListSerializer(many=True, read_only=True)

    def get_images(self, obj):
        return MediaAssetSerializer(
            [pi.asset for pi in obj.product_images.all()],
            many=True,
        ).data

    class Meta:
        model  = Product
        fields = (
            "id", "name", "sku", "slug", "category", "collection",
            "short_description", "description", "features", "tech_specs",
            "images", "pdf_catalog",
            "meta_title", "meta_description", "meta_keywords",
            "related_products", "status", "created", "updated",
        )
