from rest_framework import serializers
from .models import Category, Collection, Product, ProductImage
from media_library.models import MediaAsset


def _absolutize(url, context):
    """Turn a stored ``/media/…`` path into an absolute URL so the storefront
    (a different origin) can load it. Absolute values are returned untouched."""
    if not url or url.startswith(("http://", "https://", "//")):
        return url
    request = context.get("request") if context else None
    return request.build_absolute_uri(url) if request is not None else url


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return _absolutize(obj.url, self.context)

    class Meta:
        model  = MediaAsset
        fields = ("id", "url", "original_url", "alt_text", "title", "width", "height", "type")


class CategorySerializer(serializers.ModelSerializer):
    banner_image = MediaAssetSerializer(read_only=True)
    hero_image   = serializers.SerializerMethodField()

    def get_hero_image(self, obj):
        if obj.hero_image_url:
            return obj.hero_image_url
        return obj.banner_image.url if obj.banner_image else ""

    class Meta:
        model  = Category
        fields = (
            "id", "name", "slug", "description",
            "hero_eyebrow", "hero_image", "banner_image",
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
    """Full storefront shape — used by category listings and the all-products page."""
    primary_image   = MediaAssetSerializer(read_only=True)
    category_name   = serializers.CharField(source="category.name", read_only=True)
    category_slug   = serializers.CharField(source="category.slug", read_only=True)
    collection_name = serializers.CharField(source="collection.name", read_only=True, default="")
    image_urls      = serializers.SerializerMethodField()
    related_slugs   = serializers.SerializerMethodField()

    def get_image_urls(self, obj):
        attached = [_absolutize(pi.asset.url, self.context)
                    for pi in obj.product_images.all() if pi.asset and pi.asset.url]
        return attached or list(obj.image_urls or [])

    def get_related_slugs(self, obj):
        return list(obj.related_products.values_list("slug", flat=True))

    class Meta:
        model  = Product
        fields = (
            "id", "name", "sku", "slug",
            "category_name", "category_slug", "collection_name",
            "short_description", "description",
            "finish", "thickness", "dimensions", "surface", "application",
            "design_type", "color", "badge", "accent_color",
            "features", "tech_specs",
            "primary_image", "image_urls", "related_slugs", "status",
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    images    = serializers.SerializerMethodField()
    category  = CategorySerializer(read_only=True)
    collection = CollectionSerializer(read_only=True)
    category_name   = serializers.CharField(source="category.name", read_only=True)
    category_slug   = serializers.CharField(source="category.slug", read_only=True)
    collection_name = serializers.CharField(source="collection.name", read_only=True, default="")
    collection_slug = serializers.CharField(source="collection.slug", read_only=True, default="")
    pdf_catalog = MediaAssetSerializer(read_only=True)
    related_products = ProductListSerializer(many=True, read_only=True)
    image_urls = serializers.SerializerMethodField()

    def get_images(self, obj):
        return MediaAssetSerializer(
            [pi.asset for pi in obj.product_images.all()],
            many=True, context=self.context,
        ).data

    def get_image_urls(self, obj):
        attached = [_absolutize(pi.asset.url, self.context)
                    for pi in obj.product_images.all() if pi.asset and pi.asset.url]
        return attached or list(obj.image_urls or [])

    class Meta:
        model  = Product
        fields = (
            "id", "name", "sku", "slug", "category", "collection",
            "category_name", "category_slug", "collection_name", "collection_slug",
            "short_description", "description", "features", "tech_specs",
            "finish", "thickness", "dimensions", "surface", "application",
            "design_type", "color", "badge", "accent_color",
            "images", "image_urls", "pdf_catalog",
            "meta_title", "meta_description", "meta_keywords",
            "related_products", "status", "created", "updated",
        )
