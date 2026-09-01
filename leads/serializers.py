from rest_framework import serializers
from .models import Inquiry, Dealer


class InquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Inquiry
        fields = ("type", "name", "email", "phone", "message", "city", "source_page")


class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Dealer
        fields = ("id", "name", "contact", "email", "phone", "city", "state", "address", "lat", "lng")
