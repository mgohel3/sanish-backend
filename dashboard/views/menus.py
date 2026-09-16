"""
Menu builder — CMS-managed, hierarchical (WordPress-style) menus. A per-menu
item can nest one level deep to become a dropdown submenu. The single CMS
screen for all site navigation, including the system menus that power the
live Header, Top Bar, Mega Menu, and Footer (see ``menus.models.Menu``).
"""
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.permissions import AdminRequiredMixin
from dashboard.mixins import LoggedActionMixin
from menus.models import Menu, MenuItem


class MenuListView(AdminRequiredMixin, View):
    """The "Menus" index — every CMS-managed menu."""

    def get(self, request):
        menus = Menu.objects.all()
        return render(request, "dashboard/menus/list.html", {
            "menus": menus,
            "active_nav": "menus",
        })


class MenuCreateView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/menus/menu_form.html", {
            "menu_obj": None,
            "active_nav": "menus",
        })

    def post(self, request):
        d = request.POST
        menu = Menu.objects.create(
            slug=d["slug"].strip(),
            name=d["name"].strip(),
            description=d.get("description", "").strip(),
        )
        self.log_action("Created menu", menu)
        messages.success(request, f"Menu “{menu.name}” created. Now add its items.")
        return redirect("menu_item_list", slug=menu.slug)


class MenuEditView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, slug):
        menu = get_object_or_404(Menu, slug=slug)
        return render(request, "dashboard/menus/menu_form.html", {
            "menu_obj": menu,
            "active_nav": "menus",
        })

    def post(self, request, slug):
        menu = get_object_or_404(Menu, slug=slug)
        d = request.POST
        menu.name = d["name"].strip()
        menu.description = d.get("description", "").strip()
        menu.save()
        self.log_action("Updated menu", menu)
        messages.success(request, f"“{menu.name}” saved.")
        return redirect("menu_item_list", slug=menu.slug)


class MenuDeleteView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug):
        menu = get_object_or_404(Menu, slug=slug)
        if menu.is_system:
            messages.error(request, "System menus cannot be deleted.")
            return redirect("menu_list")
        name = menu.name
        self.log_action("Deleted menu", menu)
        menu.delete()
        messages.success(request, f"Menu “{name}” deleted.")
        return redirect("menu_list")


class MenuItemListView(AdminRequiredMixin, View):
    """Top-level items of a menu, or — when ``parent_pk`` is given — the
    submenu items nested under one of those top-level items."""

    def get(self, request, slug, parent_pk=None):
        menu = get_object_or_404(Menu, slug=slug)
        parent = get_object_or_404(MenuItem, pk=parent_pk, menu=menu) if parent_pk else None
        items = menu.items.filter(parent=parent)
        return render(request, "dashboard/menus/items.html", {
            "menu_obj": menu,
            "parent": parent,
            "items": items,
            "active_nav": "menus",
        })


class MenuItemReorderView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug, parent_pk=None):
        menu = get_object_or_404(Menu, slug=slug)
        parent = get_object_or_404(MenuItem, pk=parent_pk, menu=menu) if parent_pk else None
        try:
            order = json.loads(request.body).get("order", [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"ok": False, "error": "bad payload"}, status=400)
        for pos, pk in enumerate(order):
            MenuItem.objects.filter(pk=pk, menu=menu, parent=parent).update(position=pos)
        self.log_action(f"Reordered “{menu.name}” items", menu)
        return JsonResponse({"ok": True})


class MenuItemCreateView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, slug, parent_pk=None):
        menu = get_object_or_404(Menu, slug=slug)
        parent = get_object_or_404(MenuItem, pk=parent_pk, menu=menu) if parent_pk else None
        return render(request, "dashboard/menus/item_form.html", {
            "menu_obj": menu,
            "parent": parent,
            "item": None,
            "active_nav": "menus",
        })

    def post(self, request, slug, parent_pk=None):
        menu = get_object_or_404(Menu, slug=slug)
        parent = get_object_or_404(MenuItem, pk=parent_pk, menu=menu) if parent_pk else None
        d = request.POST
        last = menu.items.filter(parent=parent).order_by("-position").first()
        item = MenuItem.objects.create(
            menu=menu,
            parent=parent,
            label=d["label"].strip(),
            url=d.get("url", "").strip(),
            open_new_tab=("open_new_tab" in d),
            active=("active" in d),
            position=(last.position + 1) if last else 0,
        )
        self.log_action("Added menu item", item)
        messages.success(request, f"Item “{item.label}” added.")
        if parent:
            return redirect("menu_item_children", slug=slug, parent_pk=parent.pk)
        return redirect("menu_item_list", slug=slug)


class MenuItemEditView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, slug, pk):
        item = get_object_or_404(MenuItem, pk=pk, menu__slug=slug)
        return render(request, "dashboard/menus/item_form.html", {
            "menu_obj": item.menu,
            "parent": item.parent,
            "item": item,
            "active_nav": "menus",
        })

    def post(self, request, slug, pk):
        item = get_object_or_404(MenuItem, pk=pk, menu__slug=slug)
        d = request.POST
        item.label = d["label"].strip()
        item.url = d.get("url", "").strip()
        item.open_new_tab = "open_new_tab" in d
        item.active = "active" in d
        item.save()
        self.log_action("Updated menu item", item)
        messages.success(request, f"Item “{item.label}” saved.")
        if item.parent:
            return redirect("menu_item_children", slug=slug, parent_pk=item.parent.pk)
        return redirect("menu_item_list", slug=slug)


class MenuItemDeleteView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug, pk):
        item = get_object_or_404(MenuItem, pk=pk, menu__slug=slug)
        label = item.label
        parent = item.parent
        self.log_action("Deleted menu item", item)
        item.delete()
        messages.success(request, f"Item “{label}” deleted.")
        if parent:
            return redirect("menu_item_children", slug=slug, parent_pk=parent.pk)
        return redirect("menu_item_list", slug=slug)
