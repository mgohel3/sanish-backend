from rest_framework import serializers
from .models import MediaAsset, MediaFolder


class MediaFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MediaFolder
        fields = ("id", "name", "slug", "parent")


class MediaAssetSerializer(serializers.ModelSerializer):
    url          = serializers.SerializerMethodField()
    original_url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return obj.url

    def get_original_url(self, obj):
        return obj.original_url

    class Meta:
        model  = MediaAsset
        fields = ("id", "url", "original_url", "type", "folder", "alt_text",
                  "title", "caption", "description", "width", "height", "created")
