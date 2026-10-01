from rest_framework import serializers

from .models import CarpenterTestimonial


class CarpenterTestimonialSerializer(serializers.ModelSerializer):
    photo = serializers.CharField(source="photo_url", default="")

    class Meta:
        model = CarpenterTestimonial
        fields = ["id", "name", "role", "quote", "photo"]
