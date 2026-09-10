import re

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
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
    # Serve uploaded media locally, but through a Range-aware view so CMS-hosted
    # video (.mp4/.webm) plays and seeks in the browser — django.views.static
    # .serve / static() return the whole file with a 200 and no Accept-Ranges,
    # which Chrome and Safari refuse to play as a <video> source.
    from media_library.serve_dev import serve_media

    _media_prefix = re.escape(settings.MEDIA_URL.lstrip("/"))
    urlpatterns += [
        re_path(
            r"^%s(?P<path>.*)$" % _media_prefix,
            serve_media,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
