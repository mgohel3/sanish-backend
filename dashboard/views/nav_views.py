from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages

from accounts.permissions import AdminRequiredMixin
from dashboard.mixins import LoggedActionMixin
from seo.models import NavLink


class NavLinkListView(AdminRequiredMixin, View):
    def get(self, request):
        links = NavLink.objects.all()
        by_group = {}
        for lnk in links:
            by_group.setdefault(lnk.get_group_display(), []).append(lnk)
        return render(request, "dashboard/nav/list.html", {
            "by_group":  by_group,
            "all_links": links,
            "groups":    NavLink.GROUP_CHOICES,
            "active_nav": "nav_links",
        })


class NavLinkCreateView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/nav/form.html", {
            "groups": NavLink.GROUP_CHOICES,
            "active_nav": "nav_links",
        })

    def post(self, request):
        d = request.POST
        lnk = NavLink.objects.create(
            label=d["label"],
            url=d["url"],
            group=d.get("group", "main"),
            position=int(d.get("position") or 0),
            open_new_tab=bool(d.get("open_new_tab")),
            active=bool(d.get("active", True)),
        )
        self.log_action("Created nav link", lnk)
        messages.success(request, f"Nav link '{lnk.label}' created.")
        return redirect("nav_link_list")


class NavLinkEditView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        lnk = get_object_or_404(NavLink, pk=pk)
        return render(request, "dashboard/nav/form.html", {
            "link": lnk,
            "groups": NavLink.GROUP_CHOICES,
            "active_nav": "nav_links",
        })

    def post(self, request, pk):
        lnk = get_object_or_404(NavLink, pk=pk)
        d = request.POST
        lnk.label = d["label"]
        lnk.url = d["url"]
        lnk.group = d.get("group", "main")
        lnk.position = int(d.get("position") or 0)
        lnk.open_new_tab = bool(d.get("open_new_tab"))
        lnk.active = bool(d.get("active"))
        lnk.save()
        self.log_action("Updated nav link", lnk)
        messages.success(request, "Nav link updated.")
        return redirect("nav_link_list")


class NavLinkDeleteView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        lnk = get_object_or_404(NavLink, pk=pk)
        self.log_action("Deleted nav link", lnk)
        lnk.delete()
        messages.success(request, "Nav link deleted.")
        return redirect("nav_link_list")
