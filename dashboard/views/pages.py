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
from django.utils.text import slugify
from django.views import View

from accounts.permissions import AdminRequiredMixin
from dashboard.mixins import LoggedActionMixin
from dashboard.views.homepage import _parse_content
from homepage import blocks
from pages.models import PageSection, SitePage
from pages.page_templates import PAGE_TEMPLATES


class SitePageListView(AdminRequiredMixin, View):
    """The "Pages" index — every editable page."""

    def get(self, request):
        pages = SitePage.objects.all()
        return render(request, "dashboard/pages/list.html", {
            "pages": pages,
            "active_nav": "pages",
        })


class SitePageCreateView(AdminRequiredMixin, LoggedActionMixin, View):
    """Create a brand-new page, optionally seeded from a ready-made block
    template (Elementor/WordPress-theme style starting point)."""

    def get(self, request):
        return render(request, "dashboard/pages/new.html", {
            "templates": PAGE_TEMPLATES,
            "active_nav": "pages",
        })

    def post(self, request):
        d = request.POST
        title = d.get("title", "").strip()
        slug = slugify(d.get("slug") or title)
        template_key = d.get("template") or "blank"

        if not title or not slug:
            messages.error(request, "A title is required.")
            return redirect("site_page_create")
        if SitePage.objects.filter(slug=slug).exists():
            messages.error(request, f"A page with slug “{slug}” already exists.")
            return redirect("site_page_create")

        template = PAGE_TEMPLATES.get(template_key, PAGE_TEMPLATES["blank"])
        path = d.get("path", "").strip() or f"/{slug}"
        last = SitePage.objects.order_by("-position").first()

        page = SitePage.objects.create(
            slug=slug,
            title=title,
            path=path,
            description=d.get("description", "").strip(),
            position=(last.position + 1) if last else 0,
            is_system=False,  # admin-created pages can be deleted, unlike the seeded system pages
        )
        for i, (block_type, label, anchor_id, content) in enumerate(template["blocks"]):
            PageSection.objects.create(
                page=page, block_type=block_type, label=label,
                anchor_id=anchor_id, position=i, enabled=True, content=content,
            )
        self.log_action(f"Created page “{page.title}” from template “{template['label']}”", page)
        messages.success(request, f"Page “{page.title}” created with {len(template['blocks'])} starter block(s).")
        return redirect("page_section_list", slug=page.slug)


class SitePageToggleView(AdminRequiredMixin, LoggedActionMixin, View):
    """Publish / unpublish a page — draft pages 404 on the live site."""

    def post(self, request, slug):
        page = get_object_or_404(SitePage, slug=slug)
        page.is_published = not page.is_published
        page.save(update_fields=["is_published", "updated"])
        self.log_action(
            f"{'Published' if page.is_published else 'Unpublished'} page", page
        )
        messages.success(
            request,
            f"“{page.title}” is now {'published' if page.is_published else 'a draft'}.",
        )
        return redirect("site_page_list")


class SitePageDeleteView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, slug):
        page = get_object_or_404(SitePage, slug=slug)
        if page.is_system:
            messages.error(request, "System pages cannot be deleted.")
            return redirect("site_page_list")
        title = page.title
        self.log_action("Deleted page", page)
        page.delete()
        messages.success(request, f"Page “{title}” deleted.")
        return redirect("site_page_list")


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
        if block_type not in blocks.INNER_PAGE_BLOCKS:
            return render(request, "dashboard/pages/type_picker.html", {
                "page": page,
                "block_types": {k: v for k, v in blocks.BLOCK_TYPES.items() if k in blocks.INNER_PAGE_BLOCKS},
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
        if block_type not in blocks.INNER_PAGE_BLOCKS:
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
