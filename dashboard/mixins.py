"""Shared mixins used by all dashboard views."""
from accounts.permissions import (
    DashboardAccessMixin,
    ContentManagerRequiredMixin,
    SEOManagerRequiredMixin,
    SalesManagerRequiredMixin,
    AdminRequiredMixin,
    SuperAdminRequiredMixin,
)
from accounts.models import ActivityLog


class LoggedActionMixin:
    """Call self.log_action(action, obj) in any view to write to ActivityLog."""

    def log_action(self, action, obj=None):
        ActivityLog.log(
            user=self.request.user,
            action=action,
            obj=obj,
            request=self.request,
        )
