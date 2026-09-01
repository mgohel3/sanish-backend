from django.contrib.sitemaps import Sitemap
from catalog.models import Category, Collection, Product
from pages.models import CityPage
from blog.models import BlogPost


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority   = 0.8

    def items(self):
        return Product.objects.filter(status="published")

    def location(self, obj):
        return f"/products/{obj.slug}/"


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority   = 0.6

    def items(self):
        return Category.objects.filter(status="published")

    def location(self, obj):
        return f"/category/{obj.slug}/"


class CollectionSitemap(Sitemap):
    changefreq = "monthly"
    priority   = 0.6

    def items(self):
        return Collection.objects.filter(status="published")

    def location(self, obj):
        return f"/collection/{obj.slug}/"


class CityPageSitemap(Sitemap):
    changefreq = "weekly"
    priority   = 0.9

    def items(self):
        return CityPage.objects.filter(status="published")

    def location(self, obj):
        return f"/{obj.slug}/"

    def lastmod(self, obj):
        return obj.updated


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority   = 0.7

    def items(self):
        return BlogPost.objects.filter(status="published")

    def location(self, obj):
        return f"/blog/{obj.slug}/"

    def lastmod(self, obj):
        return obj.updated
