from django.contrib import admin
from .models import Category, Collection, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ("name", "slug", "status", "created")
    list_filter   = ("status",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display  = ("name", "slug", "status", "created")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model  = ProductImage
    extra  = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ("name", "sku", "category", "status", "created")
    list_filter   = ("status", "category")
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
