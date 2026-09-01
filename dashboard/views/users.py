from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.hashers import make_password

from accounts.permissions import AdminRequiredMixin, SuperAdminRequiredMixin
from accounts.models import User, ActivityLog
from dashboard.mixins import LoggedActionMixin


class UserListView(AdminRequiredMixin, View):
    def get(self, request):
        return render(request, "dashboard/users/list.html", {
            "users":      User.objects.all().order_by("-date_joined"),
            "active_nav": "users",
        })


class UserCreateView(SuperAdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/users/form.html", {
            "role_choices": User.ROLE_CHOICES,
            "active_nav":   "users",
        })

    def post(self, request):
        d = request.POST
        user = User(
            username   = d["username"],
            email      = d.get("email", ""),
            first_name = d.get("first_name", ""),
            last_name  = d.get("last_name", ""),
            role       = d.get("role", User.ROLE_CONTENT_MANAGER),
            is_staff   = True,
        )
        if d.get("password"):
            user.password = make_password(d["password"])
        user.save()
        self.log_action("Created user", user)
        messages.success(request, f"User '{user.username}' created.")
        return redirect("user_list")


class UserEditView(SuperAdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        u = get_object_or_404(User, pk=pk)
        return render(request, "dashboard/users/form.html", {
            "edit_user":    u,
            "role_choices": User.ROLE_CHOICES,
            "active_nav":   "users",
        })

    def post(self, request, pk):
        u = get_object_or_404(User, pk=pk)
        d = request.POST
        u.email      = d.get("email", u.email)
        u.first_name = d.get("first_name", u.first_name)
        u.last_name  = d.get("last_name", u.last_name)
        u.role       = d.get("role", u.role)
        if d.get("password"):
            u.password = make_password(d["password"])
        u.save()
        self.log_action("Updated user", u)
        messages.success(request, "User updated.")
        return redirect("user_list")


class ActivityLogView(AdminRequiredMixin, View):
    def get(self, request):
        logs = ActivityLog.objects.select_related("user").order_by("-timestamp")[:200]
        return render(request, "dashboard/users/activity_log.html", {
            "logs":       logs,
            "active_nav": "users",
        })
