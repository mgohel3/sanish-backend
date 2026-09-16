from rest_framework import serializers

from media_library.utils import absolutize_media_urls
from .models import GalleryCatalogue, GalleryImage


class GalleryImageSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    src = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ("id", "src")

    def get_id(self, obj):
        return obj.product_id or str(obj.pk)

    def get_src(self, obj):
        # Legacy "/assets/…" paths are served by the frontend itself and stay
        # relative; anything uploaded through the CMS Media Library ("/media/…")
        # needs absolutizing to this API's own origin so the frontend (a
        # different origin) can actually load it.
        return absolutize_media_urls(obj.image, self.context.get("request"))


def _thumbnail_for(catalogue, request):
    """Matches the old manifest logic: cover image, else the first product image."""
    if catalogue.cover_image:
        return absolutize_media_urls(catalogue.cover_image, request)
    first = catalogue.images.filter(enabled=True).first()
    return absolutize_media_urls(first.image, request) if first else ""


class GalleryCatalogueListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")
    thumbnail = serializers.SerializerMethodField()
    image_count = serializers.IntegerField(source="images.count", read_only=True)

    class Meta:
        model = GalleryCatalogue
        fields = ("slug", "name", "thumbnail", "image_count")

    def get_thumbnail(self, obj):
        return _thumbnail_for(obj, self.context.get("request"))


class GalleryCatalogueDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")
    thumbnail = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = GalleryCatalogue
        fields = ("slug", "name", "thumbnail", "images")

    def get_thumbnail(self, obj):
        return _thumbnail_for(obj, self.context.get("request"))

    def get_images(self, obj):
        return GalleryImageSerializer(
            obj.images.filter(enabled=True), many=True, context=self.context
        ).data
