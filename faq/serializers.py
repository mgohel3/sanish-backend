from rest_framework import serializers

from .models import Faq


class FaqSerializer(serializers.ModelSerializer):
    source_slug = serializers.CharField(source="source_post.slug", default=None, read_only=True)
    source_title = serializers.CharField(source="source_post.title", default=None, read_only=True)

    class Meta:
        model = Faq
        fields = ["id", "question", "answer", "source_slug", "source_title"]
