from rest_framework import serializers

from .models import Menu, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ("label", "url", "open_new_tab", "children")

    def get_children(self, obj):
        return MenuItemSerializer(obj.children.all(), many=True).data


class MenuSerializer(serializers.ModelSerializer):
    """Public payload for ``GET /api/menus/<slug>/`` — a nested item tree,
    one level of dropdown submenus deep."""

    items = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ("slug", "name", "items")

    def get_items(self, obj):
        return MenuItemSerializer(obj.items.filter(parent__isnull=True), many=True).data
