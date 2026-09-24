from rest_framework import serializers
from .models import Category, Collection, Product, ProductImage
from media_library.models import MediaAsset

# Shown on the storefront in place of a real photo whenever a product has no
# images attached. Backed by a static file (not Media Library) so it always
# resolves, in every environment, without depending on CMS content.
PLACEHOLDER_IMAGE_PATH = "/static/img/placeholder-product.webp"


def _absolutize(url, context):
    """Turn a stored ``/media/…`` path into an absolute URL so the storefront
    (a different origin) can load it. Absolute values are returned untouched."""
    if not url or url.startswith(("http://", "https://", "//")):
        return url
    request = context.get("request") if context else None
    return request.build_absolute_uri(url) if request is not None else url


def _placeholder_image(context):
    return {
        "id": None,
        "url": _absolutize(PLACEHOLDER_IMAGE_PATH, context),
        "original_url": "",
        "alt_text": "Image coming soon",
        "title": "Placeholder",
        "width": None,
        "height": None,
        "type": "image",
    }


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
    pdf_catalog = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = Collection
        fields = (
            "id", "name", "slug", "description", "images",
            "show_in_mega_menu", "mega_accent_color", "mega_position",
            "seo_title", "meta_description", "meta_keywords", "pdf_catalog", "status",
        )


class ProductListSerializer(serializers.ModelSerializer):
    """Full storefront shape — used by category listings and the all-products page."""
    primary_image   = serializers.SerializerMethodField()
    category_name   = serializers.CharField(source="category.name", read_only=True)
    category_slug   = serializers.CharField(source="category.slug", read_only=True)
    collection_name = serializers.CharField(source="collection.name", read_only=True, default="")
    image_urls      = serializers.SerializerMethodField()
    related_slugs   = serializers.SerializerMethodField()

    def _gallery_images(self, obj):
        """The view's queryset prefetches product_images__asset — obj.product_images.all()
        is served from that cache for free. Filtering in Python here (instead of the
        obj.primary_image property or a fresh .filter(role=...) call, both of which
        issue their own query and bypass the prefetch) is what actually makes that
        prefetch pay off: on the full-catalog listing endpoint this was several
        thousand redundant queries for one page load (one extra pair per product)."""
        cache = getattr(obj, "_gallery_images_cache", None)
        if cache is None:
            cache = [pi for pi in obj.product_images.all() if pi.role == ProductImage.ROLE_GALLERY]
            obj._gallery_images_cache = cache
        return cache

    def get_primary_image(self, obj):
        gallery = self._gallery_images(obj)
        if gallery:
            return MediaAssetSerializer(gallery[0].asset, context=self.context).data
        return _placeholder_image(self.context)

    def get_image_urls(self, obj):
        attached = [_absolutize(pi.asset.url, self.context)
                    for pi in self._gallery_images(obj)
                    if pi.asset and pi.asset.url]
        return attached or list(obj.image_urls or []) or [_absolutize(PLACEHOLDER_IMAGE_PATH, self.context)]

    def get_related_slugs(self, obj):
        return [p.slug for p in obj.related_products.all()]

    class Meta:
        model  = Product
        fields = (
            "id", "name", "sku", "slug",
            "category_name", "category_slug", "collection_name",
            "short_description", "description",
            "finish", "thickness", "dimensions", "surface", "application",
            "product_type", "surface_category",
            "design_type", "color", "badge", "accent_color",
            "features", "tech_specs",
            "show_thickness", "show_dimensions",
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
    application_image = serializers.SerializerMethodField()
    texture_variants = serializers.SerializerMethodField()

    def _images_by_role(self, obj):
        """Group this product's images by role from a single pass over
        obj.product_images.all() — reused by every get_*() below instead of
        each running its own .filter(role=...) query. When the view's
        queryset prefetches product_images (see ProductDetailView),
        .all() is served from that prefetch cache for free; even without
        it, this still collapses 4 separate queries into 1. Ordering
        matches the model's default (`position`), same as the old
        per-role .filter() calls."""
        cache = getattr(obj, "_images_by_role_cache", None)
        if cache is None:
            cache = {ProductImage.ROLE_GALLERY: [], ProductImage.ROLE_APPLICATION: [], ProductImage.ROLE_TEXTURE: []}
            for pi in obj.product_images.all():
                cache.setdefault(pi.role, []).append(pi)
            obj._images_by_role_cache = cache
        return cache

    def get_images(self, obj):
        data = MediaAssetSerializer(
            [pi.asset for pi in self._images_by_role(obj)[ProductImage.ROLE_GALLERY]],
            many=True, context=self.context,
        ).data
        return data or ([] if obj.image_urls else [_placeholder_image(self.context)])

    def get_image_urls(self, obj):
        attached = [_absolutize(pi.asset.url, self.context)
                    for pi in self._images_by_role(obj)[ProductImage.ROLE_GALLERY]
                    if pi.asset and pi.asset.url]
        return attached or list(obj.image_urls or []) or [_absolutize(PLACEHOLDER_IMAGE_PATH, self.context)]

    def get_application_image(self, obj):
        """The single 'applied in a room' shot, shown below the title — a Media
        Library image tagged with the Application role, falling back to the
        external application_image_url when none is attached."""
        app_images = self._images_by_role(obj)[ProductImage.ROLE_APPLICATION]
        pi = app_images[0] if app_images else None
        if pi and pi.asset and pi.asset.url:
            return _absolutize(pi.asset.url, self.context)
        return obj.application_image_url or ""

    def get_texture_variants(self, obj):
        """[{label, image}, …] texture-finish thumbnails shown near the title —
        Media Library images tagged with the Texture role, falling back to the
        external texture_variants list when none are attached."""
        texture_images = self._images_by_role(obj)[ProductImage.ROLE_TEXTURE]
        if texture_images:
            return [
                {
                    "label": pi.label or (pi.asset.title if pi.asset else ""),
                    "image": _absolutize(pi.asset.url, self.context) if pi.asset else "",
                }
                for pi in texture_images
            ]
        return [
            {"label": t.get("label", ""), "image": t.get("image_url", "")}
            for t in (obj.texture_variants or []) if isinstance(t, dict)
        ]

    class Meta:
        model  = Product
        fields = (
            "id", "name", "sku", "slug", "category", "collection",
            "category_name", "category_slug", "collection_name", "collection_slug",
            "short_description", "description", "features", "tech_specs",
            "finish", "thickness", "dimensions", "surface", "application",
            "product_type", "surface_category",
            "design_type", "color", "badge", "accent_color",
            "show_surface", "show_product_type", "show_finish", "show_surface_category",
            "show_thickness", "show_dimensions", "show_application", "show_design_type",
            "images", "image_urls", "application_image", "texture_variants", "pdf_catalog",
            "meta_title", "meta_description", "meta_keywords",
            "related_products", "status", "created", "updated",
        )
