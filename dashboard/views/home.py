from django.views.generic import TemplateView
from accounts.models import ActivityLog
from accounts.permissions import DashboardAccessMixin


class HomeView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recent_activities"] = ActivityLog.objects.select_related("user")[:20]
        ctx["active_nav"] = "home"
        return ctx
