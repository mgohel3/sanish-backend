from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from catalog.models import Category, Collection


class CategoryListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        return render(request, "dashboard/categories/list.html", {
            "categories": Category.objects.all(),
            "active_nav": "categories",
        })


class CategoryCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/categories/form.html", {"active_nav": "categories"})

    def post(self, request):
        d = request.POST
        cat = Category.objects.create(
            name=d["name"],
            description=d.get("description", ""),
            hero_eyebrow=d.get("hero_eyebrow", ""),
            hero_image_url=d.get("hero_image_url", ""),
            mega_group=d.get("mega_group", "none"),
            mega_icon=d.get("mega_icon", "◈"),
            mega_description=d.get("mega_description", ""),
            mega_position=int(d.get("mega_position") or 0),
            seo_title=d.get("seo_title", ""),
            meta_description=d.get("meta_description", ""),
            meta_keywords=d.get("meta_keywords", ""),
            status=d.get("status", "draft"),
        )
        self.log_action("Created category", cat)
        messages.success(request, f"Category '{cat.name}' created.")
        return redirect("category_list")


class CategoryEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        cat = get_object_or_404(Category, pk=pk)
        return render(request, "dashboard/categories/form.html", {"category": cat, "active_nav": "categories"})

    def post(self, request, pk):
        cat = get_object_or_404(Category, pk=pk)
        d = request.POST
        cat.name = d["name"]
        cat.description = d.get("description", "")
        cat.hero_eyebrow = d.get("hero_eyebrow", "")
        cat.hero_image_url = d.get("hero_image_url", "")
        cat.mega_group = d.get("mega_group", "none")
        cat.mega_icon = d.get("mega_icon", "◈")
        cat.mega_description = d.get("mega_description", "")
        cat.mega_position = int(d.get("mega_position") or 0)
        cat.seo_title = d.get("seo_title", "")
        cat.meta_description = d.get("meta_description", "")
        cat.meta_keywords = d.get("meta_keywords", "")
        cat.status = d.get("status", "draft")
        cat.save()
        self.log_action("Updated category", cat)
        messages.success(request, "Category updated.")
        return redirect("category_list")


class CategoryDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        cat = get_object_or_404(Category, pk=pk)
        self.log_action("Deleted category", cat)
        cat.delete()
        messages.success(request, "Category deleted.")
        return redirect("category_list")


# ── Collections ───────────────────────────────────────────────────────────────

class CollectionListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        return render(request, "dashboard/collections/list.html", {
            "collections": Collection.objects.all(),
            "active_nav": "collections",
        })


class CollectionCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/collections/form.html", {"active_nav": "collections"})

    def post(self, request):
        d = request.POST
        col = Collection.objects.create(
            name=d["name"],
            description=d.get("description", ""),
            show_in_mega_menu=bool(d.get("show_in_mega_menu")),
            mega_accent_color=d.get("mega_accent_color", "#7B9EC4"),
            mega_position=int(d.get("mega_position") or 0),
            seo_title=d.get("seo_title", ""),
            meta_description=d.get("meta_description", ""),
            meta_keywords=d.get("meta_keywords", ""),
            status=d.get("status", "draft"),
        )
        self.log_action("Created collection", col)
        messages.success(request, f"Collection '{col.name}' created.")
        return redirect("collection_list")


class CollectionEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        col = get_object_or_404(Collection, pk=pk)
        return render(request, "dashboard/collections/form.html", {"collection": col, "active_nav": "collections"})

    def post(self, request, pk):
        col = get_object_or_404(Collection, pk=pk)
        d = request.POST
        col.name = d["name"]
        col.description = d.get("description", "")
        col.show_in_mega_menu = bool(d.get("show_in_mega_menu"))
        col.mega_accent_color = d.get("mega_accent_color", "#7B9EC4")
        col.mega_position = int(d.get("mega_position") or 0)
        col.seo_title = d.get("seo_title", "")
        col.meta_description = d.get("meta_description", "")
        col.meta_keywords = d.get("meta_keywords", "")
        col.status = d.get("status", "draft")
        col.save()
        self.log_action("Updated collection", col)
        messages.success(request, "Collection updated.")
        return redirect("collection_list")


class CollectionDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        col = get_object_or_404(Collection, pk=pk)
        self.log_action("Deleted collection", col)
        col.delete()
        messages.success(request, "Collection deleted.")
        return redirect("collection_list")
