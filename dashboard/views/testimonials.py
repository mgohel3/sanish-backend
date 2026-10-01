"""Carpenter testimonials builder — the CMS-managed carousel on the public
/rewards page. Items can be added, reordered, hidden, or removed here.
A near-exact clone of dashboard.views.faq's CRUD pattern."""
import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from testimonials.models import CarpenterTestimonial

TESTIMONIALS_PER_PAGE = 20


class TestimonialListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        qs = CarpenterTestimonial.objects.all()
        total_count = qs.count()
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
            "total_count":  total_count,
            "active_nav":   "testimonials",
        })


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
        self.log_action("Reordered carpenter testimonials")
        return JsonResponse({"ok": True})


class TestimonialToggleView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        t = get_object_or_404(CarpenterTestimonial, pk=pk)
        t.is_active = not t.is_active
        t.save(update_fields=["is_active", "updated"])
        self.log_action(f"{'Enabled' if t.is_active else 'Disabled'} carpenter testimonial", t)
        messages.success(request, f"Testimonial is now {'visible' if t.is_active else 'hidden'}.")
        return redirect("testimonial_list")


class TestimonialCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/testimonials/form.html", {
            "testimonial": None,
            "active_nav":  "testimonials",
        })

    def post(self, request):
        d = request.POST
        name = d.get("name", "").strip()
        quote = d.get("quote", "").strip()
        if not name or not quote:
            messages.error(request, "Both a name and a testimonial are required.")
            return redirect("testimonial_create")
        last = CarpenterTestimonial.objects.order_by("-position").first()
        t = CarpenterTestimonial.objects.create(
            name=name,
            role=d.get("role", "").strip(),
            quote=quote,
            photo_url=d.get("photo_url", "").strip(),
            is_active=("is_active" in d),
            position=(last.position + 1) if last else 0,
        )
        self.log_action("Created carpenter testimonial", t)
        messages.success(request, "Testimonial added.")
        return redirect("testimonial_list")


class TestimonialEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        t = get_object_or_404(CarpenterTestimonial, pk=pk)
        return render(request, "dashboard/testimonials/form.html", {
            "testimonial": t,
            "active_nav":  "testimonials",
        })

    def post(self, request, pk):
        t = get_object_or_404(CarpenterTestimonial, pk=pk)
        d = request.POST
        t.name = d.get("name", "").strip()
        t.role = d.get("role", "").strip()
        t.quote = d.get("quote", "").strip()
        t.photo_url = d.get("photo_url", "").strip()
        t.is_active = "is_active" in d
        t.save()
        self.log_action("Updated carpenter testimonial", t)
        messages.success(request, "Testimonial saved.")
        return redirect("testimonial_list")


class TestimonialDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        t = get_object_or_404(CarpenterTestimonial, pk=pk)
        self.log_action("Deleted carpenter testimonial", t)
        t.delete()
        messages.success(request, "Testimonial deleted.")
        return redirect("testimonial_list")
