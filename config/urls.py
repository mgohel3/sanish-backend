from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from seo.sitemaps import (
    ProductSitemap, CategorySitemap, CollectionSitemap,
    CityPageSitemap, BlogSitemap,
)

sitemaps = {
    "products":    ProductSitemap,
    "categories":  CategorySitemap,
    "collections": CollectionSitemap,
    "city_pages":  CityPageSitemap,
    "blog":        BlogSitemap,
}

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("cms/",   include("dashboard.urls")),
    path("api/",   include("api.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
