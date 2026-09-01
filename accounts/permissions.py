"""Role-based permission mixins for dashboard views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class DashboardAccessMixin(LoginRequiredMixin):
    """Base: requires login + is_staff or has a CMS role."""
    login_url = "/cms/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_superuser or hasattr(request.user, "role")):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SuperAdminRequiredMixin(DashboardAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        sup = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and not request.user.is_super_admin and not request.user.is_superuser:
            raise PermissionDenied
        return sup


class AdminRequiredMixin(DashboardAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        sup = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and not (request.user.is_admin_or_above or request.user.is_superuser):
            raise PermissionDenied
        return sup


class SEOManagerRequiredMixin(DashboardAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        sup = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and not (request.user.can_manage_seo or request.user.is_superuser):
            raise PermissionDenied
        return sup


class ContentManagerRequiredMixin(DashboardAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        sup = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and not (request.user.can_manage_content or request.user.is_superuser):
            raise PermissionDenied
        return sup


class SalesManagerRequiredMixin(DashboardAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        sup = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and not (request.user.can_manage_leads or request.user.is_superuser):
            raise PermissionDenied
        return sup
