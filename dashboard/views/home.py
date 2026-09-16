from django.db.models import Count, Q
from django.views.generic import TemplateView
from accounts.models import ActivityLog
from accounts.permissions import DashboardAccessMixin
from catalog.models import Product, Collection
from leads.models import Inquiry


class HomeView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recent_activities"] = ActivityLog.objects.select_related("user")[:6]
        ctx["recent_inquiries"] = Inquiry.objects.filter(status="new")[:5]
        ctx["active_nav"] = "home"

        total_products = Product.objects.count()
        published_products = Product.objects.filter(status=Product.STATUS_PUBLISHED).count()
        draft_products = Product.objects.filter(status=Product.STATUS_DRAFT).count()
        collections = Collection.objects.annotate(
            product_count=Count("products"),
            published_count=Count("products", filter=Q(products__status=Product.STATUS_PUBLISHED)),
        ).order_by("-product_count")

        ctx["product_overview"] = {
            "total": total_products,
            "published": published_products,
            "draft": draft_products,
            "published_pct": round(published_products / total_products * 100) if total_products else 0,
            "collections": collections,
        }
        return ctx
