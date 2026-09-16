from django.conf import settings

from catalog.models import Product, Category, Collection
from pages.models import CityPage
from leads.models import Inquiry
from blog.models import BlogPost


def dashboard_context(request):
    if not request.path.startswith("/cms/") or not request.user.is_authenticated:
        return {}
    return {
        "FRONTEND_URL": settings.FRONTEND_URL,
        "stats": {
            "products":       Product.objects.count(),
            "categories":     Category.objects.count(),
            "collections":    Collection.objects.count(),
            "city_pages":     CityPage.objects.count(),
            "inquiries":      Inquiry.objects.filter(status="new").count(),
            "blog_posts":     BlogPost.objects.count(),
            "draft_products": Product.objects.filter(status="draft").count(),
            "draft_blog":     BlogPost.objects.filter(status="draft").count(),
            "draft_cities":   CityPage.objects.filter(status="draft").count(),
        },
    }
