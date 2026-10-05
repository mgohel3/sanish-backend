"""Testimonials builder — CMS-managed carousels. Entries live in editor-defined
CATEGORIES (tabs: Carpenters, Clients, … add more any time); the "Client
Testimonials" page block picks which category to show. Items can be added,
reordered, hidden, moved between categories, or removed here.
A near-exact clone of dashboard.views.faq's CRUD pattern."""
import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from testimonials.models import CarpenterTestimonial, TestimonialCategory

TESTIMONIALS_PER_PAGE = 20


def _list_url(category):
    return f"{reverse('testimonial_list')}?cat={category.pk}" if category else reverse("testimonial_list")


def _current_category(request, categories):
    raw = request.GET.get("cat") or request.POST.get("category") or ""
    if str(raw).isdigit():
        for c in categories:
            if c.pk == int(raw):
                return c
    return categories[0] if categories else None


class TestimonialListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        categories = list(TestimonialCategory.objects.all())
        for c in categories:
            c.total = c.testimonials.count()
        current = _current_category(request, categories)
        qs = current.testimonials.all() if current else CarpenterTestimonial.objects.none()
        paginator = Paginator(qs, TESTIMONIALS_PER_PAGE)
        page_obj = paginator.get_page(request.GET.get("page"))
        elided_pages = list(paginator.get_elided_page_range(
            page_obj.number, on_each_side=2, on_ends=1
        ))
        return render(request, "dashboard/testimonials/list.html", {
            "testimonials": page_obj,
            "page_obj":     page_obj,
            "paginator":    paginator,
            "elided_pages": elided_pages,
            "categories":   categories,
            "current":      current,
            "total_count":  current.total if current else 0,
            "active_nav":   "testimonials",
        })


class TestimonialCategoryCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request):
        name = request.POST.get("name", "").strip()[:80]
        if not name:
            messages.error(request, "Give the new category a name.")
            return redirect("testimonial_list")
        existing = TestimonialCategory.objects.filter(name__iexact=name).first()
        if existing:
            messages.info(request, f"“{existing.name}” already exists.")
            return redirect(_list_url(existing))
        last = TestimonialCategory.objects.order_by("-position").first()
        cat = TestimonialCategory.objects.create(name=name, position=(last.position + 1) if last else 0)
        self.log_action("Created testimonial category", cat)
        messages.success(request, f"Category “{cat.name}” added — now add testimonials to it.")
        return redirect(_list_url(cat))


class TestimonialCategoryRenameView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        cat = get_object_or_404(TestimonialCategory, pk=pk)
        name = request.POST.get("name", "").strip()[:80]
        if not name or name == cat.name:
            return redirect(_list_url(cat))
        if TestimonialCategory.objects.filter(name__iexact=name).exclude(pk=cat.pk).exists():
            messages.error(request, f"Another category is already called “{name}”.")
            return redirect(_list_url(cat))
        old = cat.name
        cat.name = name
        cat.save(update_fields=["name"])
        # Keep any page block that points at this category by name working.
        from homepage.models import HomeSection
        from pages.models import PageSection
        for Model in (HomeSection, PageSection):
            for s in Model.objects.filter(block_type="client_testimonials"):
                if isinstance(s.content, dict) and s.content.get("category") == old:
                    s.content = {**s.content, "category": name}
                    s.save()
        self.log_action(f"Renamed testimonial category “{old}”", cat)
        messages.success(request, f"Renamed to “{name}”.")
        return redirect(_list_url(cat))


class TestimonialCategoryDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        cat = get_object_or_404(TestimonialCategory, pk=pk)
        if cat.testimonials.exists():
            messages.error(
                request,
                f"“{cat.name}” still has testimonials. Move or delete them first, then delete the category.",
            )
            return redirect(_list_url(cat))
        self.log_action("Deleted testimonial category", cat)
        name = cat.name
        cat.delete()
        messages.success(request, f"Category “{name}” deleted.")
        return redirect("testimonial_list")


class TestimonialReorderView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request):
        try:
            order = [int(pk) for pk in json.loads(request.body).get("order", [])]
        except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "bad payload"}, status=400)
        if not order:
            return JsonResponse({"ok": True})
        existing = CarpenterTestimonial.objects.filter(pk__in=order).values_list("position", flat=True)
        base = min(existing, default=0)
        for offset, pk in enumerate(order):
            CarpenterTestimonial.objects.filter(pk=pk).update(position=base + offset)
        self.log_action("Reordered testimonials")
        return JsonResponse({"ok": True})


class TestimonialToggleView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        t = get_object_or_404(CarpenterTestimonial, pk=pk)
        t.is_active = not t.is_active
        t.save(update_fields=["is_active", "updated"])
        self.log_action(f"{'Enabled' if t.is_active else 'Disabled'} testimonial", t)
        messages.success(request, f"Testimonial is now {'visible' if t.is_active else 'hidden'}.")
        return redirect(_list_url(t.category))


class TestimonialCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        categories = list(TestimonialCategory.objects.all())
        return render(request, "dashboard/testimonials/form.html", {
            "testimonial": None,
            "categories":  categories,
            "current":     _current_category(request, categories),
            "active_nav":  "testimonials",
        })

    def post(self, request):
        d = request.POST
        categories = list(TestimonialCategory.objects.all())
        category = _current_category(request, categories)
        name = d.get("name", "").strip()
        quote = d.get("quote", "").strip()
        if not name or not quote:
            messages.error(request, "Both a name and a testimonial are required.")
            return redirect(f"{reverse('testimonial_create')}?cat={category.pk}" if category else "testimonial_create")
        last = CarpenterTestimonial.objects.order_by("-position").first()
        t = CarpenterTestimonial.objects.create(
            category=category,
            name=name,
            role=d.get("role", "").strip(),
            quote=quote,
            photo_url=d.get("photo_url", "").strip(),
            is_active=("is_active" in d),
            position=(last.position + 1) if last else 0,
        )
        self.log_action("Created testimonial", t)
        messages.success(request, "Testimonial added.")
        return redirect(_list_url(category))


class TestimonialEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        t = get_object_or_404(CarpenterTestimonial, pk=pk)
        return render(request, "dashboard/testimonials/form.html", {
            "testimonial": t,
            "categories":  list(TestimonialCategory.objects.all()),
            "current":     t.category,
            "active_nav":  "testimonials",
        })

    def post(self, request, pk):
        t = get_object_or_404(CarpenterTestimonial, pk=pk)
        d = request.POST
        categories = list(TestimonialCategory.objects.all())
        t.category = _current_category(request, categories) or t.category
        t.name = d.get("name", "").strip()
        t.role = d.get("role", "").strip()
        t.quote = d.get("quote", "").strip()
        t.photo_url = d.get("photo_url", "").strip()
        t.is_active = "is_active" in d
        t.save()
        self.log_action("Updated testimonial", t)
        messages.success(request, "Testimonial saved.")
        return redirect(_list_url(t.category))


class TestimonialDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        t = get_object_or_404(CarpenterTestimonial, pk=pk)
        cat = t.category
        self.log_action("Deleted testimonial", t)
        t.delete()
        messages.success(request, "Testimonial deleted.")
        return redirect(_list_url(cat))
