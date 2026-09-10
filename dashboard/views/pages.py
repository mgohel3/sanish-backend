"""
Pages builder — manage the ordered blocks that make up each CMS-managed site
page (About Us, Contact Us, Rewards, …). A per-page clone of
``dashboard.views.homepage``; blocks share ``homepage.blocks.BLOCK_TYPES`` and
the same generic form/list templates.
"""
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.permissions import AdminRequiredMixin
from dashboard.mixins import LoggedActionMixin
from dashboard.views.homepage import _parse_content
from homepage import blocks
from pages.models import PageSection, SitePage


class SitePageListView(AdminRequiredMixin, View):
    """The "Pages" index — every editable page."""

    def get(self, request):
        pages = SitePage.objects.all()
        return render(request, "dashboard/pages/list.html", {
            "pages": pages,
            "active_nav": "pages",
        })


class PageSectionListView(AdminRequiredMixin, View):
    def get(self, request, slug):
        page = get_object_or_404(SitePage, slug=slug)
        if page.external_url_name:
            return redirect(page.external_url_name)
        return render(request, "dashboard/pages/sections.html", {
            "page": page,
            "sections": page.sections.all(),
            "active_nav": "pages",
        })


class PageSectionReorderView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug):
        page = get_object_or_404(SitePage, slug=slug)
        try:
            order = json.loads(request.body).get("order", [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"ok": False, "error": "bad payload"}, status=400)
        for pos, pk in enumerate(order):
            PageSection.objects.filter(pk=pk, page=page).update(position=pos)
        self.log_action(f"Reordered “{page.title}” sections", page)
        return JsonResponse({"ok": True})


class PageSectionToggleView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug, pk):
        section = get_object_or_404(PageSection, pk=pk, page__slug=slug)
        section.enabled = not section.enabled
        section.save(update_fields=["enabled", "updated"])
        self.log_action(
            f"{'Enabled' if section.enabled else 'Disabled'} page section", section
        )
        messages.success(
            request,
            f"“{section.label}” is now {'visible' if section.enabled else 'hidden'}.",
        )
        return redirect("page_section_list", slug=slug)


class PageSectionCreateView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, slug):
        page = get_object_or_404(SitePage, slug=slug)
        block_type = request.GET.get("type")
        if block_type not in blocks.BLOCK_TYPES:
            return render(request, "dashboard/pages/type_picker.html", {
                "page": page,
                "block_types": blocks.BLOCK_TYPES,
                "generic_blocks": blocks.GENERIC_BLOCKS,
                "active_nav": "pages",
            })
        cfg = blocks.BLOCK_TYPES[block_type]
        return render(request, "dashboard/pages/form.html", {
            "page": page,
            "block_type": block_type,
            "config": cfg,
            "values": blocks.defaults_for(block_type),
            "section": None,
            "active_nav": "pages",
        })

    def post(self, request, slug):
        page = get_object_or_404(SitePage, slug=slug)
        block_type = request.POST.get("block_type")
        if block_type not in blocks.BLOCK_TYPES:
            messages.error(request, "Unknown block type.")
            return redirect("page_section_create", slug=slug)
        last = page.sections.order_by("-position").first()
        section = PageSection.objects.create(
            page=page,
            block_type=block_type,
            label=request.POST.get("label") or blocks.BLOCK_TYPES[block_type]["label"],
            anchor_id=request.POST.get("anchor_id", "").strip(),
            enabled=("enabled" in request.POST),
            position=(last.position + 1) if last else 0,
            content=_parse_content(block_type, request.POST),
        )
        self.log_action("Created page section", section)
        messages.success(request, f"Block “{section.label}” added.")
        return redirect("page_section_list", slug=slug)


class PageSectionEditView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, slug, pk):
        section = get_object_or_404(PageSection, pk=pk, page__slug=slug)
        return render(request, "dashboard/pages/form.html", {
            "page": section.page,
            "block_type": section.block_type,
            "config": section.block_config,
            "values": section.resolved(),
            "section": section,
            "active_nav": "pages",
        })

    def post(self, request, slug, pk):
        section = get_object_or_404(PageSection, pk=pk, page__slug=slug)
        section.label = request.POST.get("label") or section.label
        section.anchor_id = request.POST.get("anchor_id", "").strip()
        section.enabled = "enabled" in request.POST
        section.content = _parse_content(section.block_type, request.POST)
        section.save()
        self.log_action("Updated page section", section)
        messages.success(request, f"Block “{section.label}” saved.")
        return redirect("page_section_list", slug=slug)


class PageSectionDeleteView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug, pk):
        section = get_object_or_404(PageSection, pk=pk, page__slug=slug)
        label = section.label
        self.log_action("Deleted page section", section)
        section.delete()
        messages.success(request, f"Block “{label}” deleted.")
        return redirect("page_section_list", slug=slug)
