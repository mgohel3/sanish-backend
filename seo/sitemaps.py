from django.contrib.sitemaps import Sitemap
from catalog.models import Category, Collection, Product
from pages.models import CityPage
from blog.models import BlogPost

# Only these 3 categories have an actual live frontend route — "Decorative
# Laminates" and "High Pressure Laminates" are unused legacy seed rows with
# nowhere real to link to (confirmed: every URL the old CategorySitemap
# generated for them 404'd). Mirrors sanish-next's CATEGORY_SLUG_TO_ROUTE
# (src/lib/catalog.ts) — the one place this mapping is otherwise encoded.
CATEGORY_SLUG_TO_ROUTE = {
    "laminates": "laminates",
    "louvers": "louvers",
    "thermo-laminates": "asa-sheets",
}


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority   = 0.8

    def items(self):
        return Product.objects.filter(status="published").select_related("category", "collection")

    def location(self, obj):
        # Mirrors sanish-next's productHref() (src/lib/catalog.ts) exactly —
        # the category segment is the category's own slug as-is (NOT run
        # through CATEGORY_SLUG_TO_ROUTE; that mapping is only for a
        # category's own *listing* page, not the segment embedded in a
        # product's URL). Was previously just "/products/<slug>/" with no
        # category/collection at all — every product URL in the sitemap
        # needed 2 redirects to reach the real page.
        cat = obj.category.slug if obj.category_id else "laminates"
        col = obj.collection.slug if obj.collection_id else "none"
        return f"/products/{cat}/{col}/{obj.slug}"


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority   = 0.6

    def items(self):
        return Category.objects.filter(status="published", slug__in=CATEGORY_SLUG_TO_ROUTE)

    def location(self, obj):
        # Was "/category/<slug>/" — not a route that exists anywhere on the
        # frontend (categories are listed at /laminates, /louvers,
        # /asa-sheets), so every entry 404'd regardless of which category.
        return f"/{CATEGORY_SLUG_TO_ROUTE[obj.slug]}"


class CollectionSitemap(Sitemap):
    """Deliberately empty for now. A collection isn't its own page — it's a
    `?collection=<slug>` filter on its category's listing page (see
    sanish-next's collectionHref()), and that slug mapping (i) isn't the
    same as Collection.slug (e.g. Perspective V4's is "08mm", not
    "perspective-v4") and (ii) doesn't exist at all yet for every collection
    (Thermo ASA has no filter slug on the frontend since it's the only
    collection in its category). Replicating that frontend-only, easily-
    stale mapping here to build a filtered-listing URL isn't worth it: every
    collection's actual products are already fully represented in the
    sitemap via ProductSitemap's own canonical URLs, which include the
    collection. The old version pointed at "/collection/<slug>/", a route
    that doesn't exist either — every entry also 404'd."""
    changefreq = "monthly"
    priority   = 0.6

    def items(self):
        return Collection.objects.none()

    def location(self, obj):
        return f"/collection/{obj.slug}"


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
