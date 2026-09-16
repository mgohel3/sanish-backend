"""
Applications (use-case) management — categories and case-study projects
shown on /applications and /applications/<category>. Modeled after the
Products/Categories CRUD pattern (catalog app), since the client asked for
"application page management... like products".
"""
import json

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from applications.models import ApplicationCategory, ApplicationProject


def _parse_repeater(post, name):
    raw = post.get(f"{name}_json", "").strip()
    try:
        rows = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        rows = []
    return [r for r in rows if any(str(v).strip() for v in r.values())]


# Repeater field configs for the project form (consumed by
# dashboard/homepage/_repeater.html, the same generic Alpine repeater used by
# the block builder — kept here rather than a shared registry since these are
# specific to ApplicationProject's fixed JSON fields).
GALLERY_FIELD = {"name": "gallery", "label": "Gallery Images", "fields": [
    {"name": "image", "type": "image", "label": "Image"},
]}
HIGHLIGHTS_FIELD = {"name": "highlights", "label": "Highlights", "fields": [
    {"name": "text", "type": "text", "label": "Highlight"},
]}
PRODUCTS_FIELD = {"name": "products", "label": "Products Used", "fields": [
    {"name": "name", "type": "text", "label": "Product name"},
    {"name": "code", "type": "text", "label": "Code"},
    {"name": "collection", "type": "text", "label": "Collection"},
    {"name": "finish", "type": "text", "label": "Finish"},
    {"name": "usage", "type": "text", "label": "Usage"},
    {"name": "product_slug", "type": "text", "label": "Product slug (optional)"},
]}


def _project_form_context(project=None):
    return {
        "project": project,
        "categories": ApplicationCategory.objects.all(),
        "gallery_field": GALLERY_FIELD,
        "highlights_field": HIGHLIGHTS_FIELD,
        "products_field": PRODUCTS_FIELD,
        "values": {
            "gallery": project.gallery if project else [],
            "highlights": project.highlights if project else [],
            "products": project.products if project else [],
        },
        "active_nav": "application_projects",
    }


# ── Categories ────────────────────────────────────────────────────────────────

CATEGORY_GALLERY_FIELD = {"name": "gallery", "label": "Gallery Images", "fields": [
    {"name": "image", "type": "image", "label": "Image"},
    {"name": "caption", "type": "text", "label": "Caption (optional)"},
]}


def _category_form_context(category=None):
    return {
        "category": category,
        "gallery_field": CATEGORY_GALLERY_FIELD,
        "values": {"gallery": category.gallery if category else []},
        "active_nav": "applications",
    }


class ApplicationCategoryListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        return render(request, "dashboard/applications/category_list.html", {
            "categories": ApplicationCategory.objects.all(),
            "active_nav": "applications",
        })


class ApplicationCategoryCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/applications/category_form.html", _category_form_context())

    def post(self, request):
        d = request.POST
        last = ApplicationCategory.objects.order_by("-position").first()
        cat = ApplicationCategory.objects.create(
            slug=d["slug"].strip(),
            label=d["label"].strip(),
            description=d.get("description", "").strip(),
            accent=d.get("accent", "").strip(),
            image=d.get("image", "").strip(),
            gallery=_parse_repeater(d, "gallery"),
            position=(last.position + 1) if last else 0,
            enabled=("enabled" in d),
        )
        self.log_action("Created application category", cat)
        messages.success(request, f"Category “{cat.label}” created.")
        return redirect("application_category_list")


class ApplicationCategoryEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        cat = get_object_or_404(ApplicationCategory, pk=pk)
        return render(request, "dashboard/applications/category_form.html", _category_form_context(cat))

    def post(self, request, pk):
        cat = get_object_or_404(ApplicationCategory, pk=pk)
        d = request.POST
        cat.label = d["label"].strip()
        cat.description = d.get("description", "").strip()
        cat.accent = d.get("accent", "").strip()
        cat.image = d.get("image", "").strip()
        cat.gallery = _parse_repeater(d, "gallery")
        cat.enabled = "enabled" in d
        cat.save()
        self.log_action("Updated application category", cat)
        messages.success(request, f"“{cat.label}” saved.")
        return redirect("application_category_list")


class ApplicationCategoryDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        cat = get_object_or_404(ApplicationCategory, pk=pk)
        if cat.projects.exists():
            messages.error(request, f"“{cat.label}” still has projects — move or delete those first.")
            return redirect("application_category_list")
        label = cat.label
        self.log_action("Deleted application category", cat)
        cat.delete()
        messages.success(request, f"Category “{label}” deleted.")
        return redirect("application_category_list")


# ── Projects (case studies) ───────────────────────────────────────────────────

class ApplicationProjectListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        category_id = request.GET.get("category", "")
        qs = ApplicationProject.objects.select_related("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return render(request, "dashboard/applications/project_list.html", {
            "projects": qs,
            "categories": ApplicationCategory.objects.all(),
            "selected_category": category_id,
            "active_nav": "application_projects",
        })


class ApplicationProjectCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/applications/project_form.html", _project_form_context())

    def post(self, request):
        d = request.POST
        last = ApplicationProject.objects.order_by("-position").first()
        project = ApplicationProject.objects.create(
            slug=d["slug"].strip(),
            label=d["label"].strip(),
            category_id=d["category"],
            finish=d.get("finish", "").strip(),
            image=d.get("image", "").strip(),
            tall=("tall" in d),
            description=d.get("description", "").strip(),
            location=d.get("location", "").strip(),
            year=d.get("year", "").strip(),
            designer=d.get("designer", "").strip(),
            area=d.get("area", "").strip(),
            gallery=_parse_repeater(d, "gallery"),
            highlights=_parse_repeater(d, "highlights"),
            products=_parse_repeater(d, "products"),
            position=(last.position + 1) if last else 0,
            enabled=("enabled" in d),
        )
        self.log_action("Created application project", project)
        messages.success(request, f"Project “{project.label}” created.")
        return redirect("application_project_list")


class ApplicationProjectEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(ApplicationProject, pk=pk)
        return render(request, "dashboard/applications/project_form.html", _project_form_context(project))

    def post(self, request, pk):
        project = get_object_or_404(ApplicationProject, pk=pk)
        d = request.POST
        project.label = d["label"].strip()
        project.category_id = d["category"]
        project.finish = d.get("finish", "").strip()
        project.image = d.get("image", "").strip()
        project.tall = "tall" in d
        project.description = d.get("description", "").strip()
        project.location = d.get("location", "").strip()
        project.year = d.get("year", "").strip()
        project.designer = d.get("designer", "").strip()
        project.area = d.get("area", "").strip()
        project.gallery = _parse_repeater(d, "gallery")
        project.highlights = _parse_repeater(d, "highlights")
        project.products = _parse_repeater(d, "products")
        project.enabled = "enabled" in d
        project.save()
        self.log_action("Updated application project", project)
        messages.success(request, f"“{project.label}” saved.")
        return redirect("application_project_list")


class ApplicationProjectDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(ApplicationProject, pk=pk)
        label = project.label
        self.log_action("Deleted application project", project)
        project.delete()
        messages.success(request, f"Project “{label}” deleted.")
        return redirect("application_project_list")
