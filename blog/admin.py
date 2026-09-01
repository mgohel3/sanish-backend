from django.contrib import admin
from .models import BlogPost, BlogCategory, Tag


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display  = ("title", "author", "status", "created")
    list_filter   = ("status", "categories")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
