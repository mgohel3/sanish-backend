"""FAQ page builder — the CMS-managed list of question/answer pairs behind
the public /faq page. Seeded from blog posts (see faq/migrations), but items
can also be added, edited, reordered, or hidden directly here."""
import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.permissions import ContentManagerRequiredMixin
from blog.models import BlogPost
from dashboard.mixins import LoggedActionMixin
from faq.models import Faq

FAQS_PER_PAGE = 20


class FaqListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        qs = Faq.objects.select_related("source_post")
        total_count = qs.count()
        paginator = Paginator(qs, FAQS_PER_PAGE)
        page_obj = paginator.get_page(request.GET.get("page"))
        elided_pages = list(paginator.get_elided_page_range(
            page_obj.number, on_each_side=2, on_ends=1
        ))
        return render(request, "dashboard/faqs/list.html", {
            "faqs":        page_obj,
            "page_obj":    page_obj,
            "paginator":   paginator,
            "elided_pages": elided_pages,
            "total_count": total_count,
            "active_nav":  "faqs",
        })


class FaqReorderView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request):
        try:
            order = [int(pk) for pk in json.loads(request.body).get("order", [])]
        except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "bad payload"}, status=400)
        if not order:
            return JsonResponse({"ok": True})
        # Only one page's worth of rows is ever reordered at a time (the
        # list is paginated), so re-slot them into the position range they
        # already occupy rather than resetting to 0 — otherwise saving a
        # reorder on page 2 would collide with page 1's positions.
        existing = Faq.objects.filter(pk__in=order).values_list("position", flat=True)
        base = min(existing, default=0)
        for offset, pk in enumerate(order):
            Faq.objects.filter(pk=pk).update(position=base + offset)
        self.log_action("Reordered FAQs")
        return JsonResponse({"ok": True})


class FaqToggleView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        faq = get_object_or_404(Faq, pk=pk)
        faq.is_active = not faq.is_active
        faq.save(update_fields=["is_active", "updated"])
        self.log_action(f"{'Enabled' if faq.is_active else 'Disabled'} FAQ", faq)
        messages.success(request, f"FAQ is now {'visible' if faq.is_active else 'hidden'}.")
        return redirect("faq_list")


class FaqCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/faqs/form.html", {
            "faq": None,
            "posts": BlogPost.objects.order_by("title"),
            "active_nav": "faqs",
        })

    def post(self, request):
        d = request.POST
        question = d.get("question", "").strip()
        answer = d.get("answer", "").strip()
        if not question or not answer:
            messages.error(request, "Both a question and an answer are required.")
            return redirect("faq_create")
        last = Faq.objects.order_by("-position").first()
        source_id = d.get("source_post")
        faq = Faq.objects.create(
            question=question,
            answer=answer,
            source_post=BlogPost.objects.filter(pk=source_id).first() if source_id else None,
            is_active=("is_active" in d),
            position=(last.position + 1) if last else 0,
        )
        self.log_action("Created FAQ", faq)
        messages.success(request, "FAQ added.")
        return redirect("faq_list")


class FaqEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        faq = get_object_or_404(Faq, pk=pk)
        return render(request, "dashboard/faqs/form.html", {
            "faq": faq,
            "posts": BlogPost.objects.order_by("title"),
            "active_nav": "faqs",
        })

    def post(self, request, pk):
        faq = get_object_or_404(Faq, pk=pk)
        d = request.POST
        faq.question = d.get("question", "").strip()
        faq.answer = d.get("answer", "").strip()
        source_id = d.get("source_post")
        faq.source_post = BlogPost.objects.filter(pk=source_id).first() if source_id else None
        faq.is_active = "is_active" in d
        faq.save()
        self.log_action("Updated FAQ", faq)
        messages.success(request, "FAQ saved.")
        return redirect("faq_list")


class FaqDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        faq = get_object_or_404(Faq, pk=pk)
        self.log_action("Deleted FAQ", faq)
        faq.delete()
        messages.success(request, "FAQ deleted.")
        return redirect("faq_list")
