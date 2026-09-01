from catalog.models import Product, Category, Collection
from pages.models import CityPage
from leads.models import Inquiry


def dashboard_context(request):
    if not request.path.startswith("/cms/") or not request.user.is_authenticated:
        return {}
    return {
        "stats": {
            "products":    Product.objects.count(),
            "categories":  Category.objects.count(),
            "collections": Collection.objects.count(),
            "city_pages":  CityPage.objects.count(),
            "inquiries":   Inquiry.objects.filter(status="new").count(),
        },
    }
