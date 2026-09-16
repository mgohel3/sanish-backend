from rest_framework import serializers
from seo.recaptcha import verify_recaptcha
from .models import Inquiry, Dealer


class InquiryCreateSerializer(serializers.ModelSerializer):
    recaptcha_token = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model  = Inquiry
        fields = ("type", "name", "email", "phone", "message", "city", "source_page", "recaptcha_token")

    def validate(self, attrs):
        token = attrs.pop("recaptcha_token", "")
        request = self.context.get("request")
        remote_ip = request.META.get("REMOTE_ADDR") if request else None
        ok, error = verify_recaptcha(token, remote_ip)
        if not ok:
            raise serializers.ValidationError({"recaptcha_token": error})
        return attrs


class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Dealer
        fields = ("id", "name", "contact", "email", "phone", "city", "state", "address", "lat", "lng")
