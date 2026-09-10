"""
Home Page block manager — reorder, enable/disable, edit and add the blocks that
make up the public home page. Content is stored on ``HomeSection.content`` (JSON)
and shaped by ``homepage.blocks.BLOCK_TYPES``.
"""
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.permissions import AdminRequiredMixin
from dashboard.mixins import LoggedActionMixin
from homepage import blocks
from homepage.models import HomeSection

SCALAR_TYPES = {"text", "textarea", "richtext", "url", "image", "video", "media", "select"}


def _parse_content(block_type, post):
    """Turn a submitted form into a ``content`` dict for the given block type."""
    cfg = blocks.BLOCK_TYPES.get(block_type, {})
    content = {}
    for field in cfg.get("fields", []):
        name = field["name"]
        ftype = field["type"]
        if ftype == "repeater":
            raw = post.get(f"{name}_json", "").strip()
            try:
                rows = json.loads(raw) if raw else []
            except json.JSONDecodeError:
                rows = []
            content[name] = [r for r in rows if any(str(v).strip() for v in r.values())]
        elif ftype == "bool":
            content[name] = name in post
        elif ftype == "number":
            val = post.get(name, "").strip()
            content[name] = (float(val) if "." in val else int(val)) if val else None
        elif ftype in SCALAR_TYPES:
            content[name] = post.get(name, "").strip()
    return content


class HomeSectionListView(AdminRequiredMixin, View):
    def get(self, request):
        sections = HomeSection.objects.all()
        return render(request, "dashboard/homepage/list.html", {
            "sections": sections,
            "block_types": blocks.BLOCK_TYPES,
            "active_nav": "homepage",
        })


class HomeSectionReorderView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request):
        try:
            order = json.loads(request.body).get("order", [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"ok": False, "error": "bad payload"}, status=400)
        for pos, pk in enumerate(order):
            HomeSection.objects.filter(pk=pk).update(position=pos)
        self.log_action("Reordered home sections")
        return JsonResponse({"ok": True})


class HomeSectionToggleView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        section = get_object_or_404(HomeSection, pk=pk)
        section.enabled = not section.enabled
        section.save(update_fields=["enabled", "updated"])
        self.log_action(
            f"{'Enabled' if section.enabled else 'Disabled'} home section", section
        )
        messages.success(
            request,
            f"“{section.label}” is now {'visible' if section.enabled else 'hidden'}.",
        )
        return redirect("home_section_list")


class HomeSectionCreateView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        block_type = request.GET.get("type")
        if block_type not in blocks.BLOCK_TYPES:
            return render(request, "dashboard/homepage/type_picker.html", {
                "block_types": blocks.BLOCK_TYPES,
                "generic_blocks": blocks.GENERIC_BLOCKS,
                "active_nav": "homepage",
            })
        cfg = blocks.BLOCK_TYPES[block_type]
        return render(request, "dashboard/homepage/form.html", {
            "block_type": block_type,
            "config": cfg,
            "values": blocks.defaults_for(block_type),
            "section": None,
            "active_nav": "homepage",
        })

    def post(self, request):
        block_type = request.POST.get("block_type")
        if block_type not in blocks.BLOCK_TYPES:
            messages.error(request, "Unknown block type.")
            return redirect("home_section_create")
        last = HomeSection.objects.order_by("-position").first()
        section = HomeSection.objects.create(
            block_type=block_type,
            label=request.POST.get("label") or blocks.BLOCK_TYPES[block_type]["label"],
            anchor_id=request.POST.get("anchor_id", "").strip(),
            enabled=("enabled" in request.POST),
            position=(last.position + 1) if last else 0,
            content=_parse_content(block_type, request.POST),
        )
        self.log_action("Created home section", section)
        messages.success(request, f"Block “{section.label}” added.")
        return redirect("home_section_list")


class HomeSectionEditView(AdminRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        section = get_object_or_404(HomeSection, pk=pk)
        return render(request, "dashboard/homepage/form.html", {
            "block_type": section.block_type,
            "config": section.block_config,
            "values": section.resolved(),
            "section": section,
            "active_nav": "homepage",
        })

    def post(self, request, pk):
        section = get_object_or_404(HomeSection, pk=pk)
        section.label = request.POST.get("label") or section.label
        section.anchor_id = request.POST.get("anchor_id", "").strip()
        section.enabled = "enabled" in request.POST
        section.content = _parse_content(section.block_type, request.POST)
        section.save()
        self.log_action("Updated home section", section)
        messages.success(request, f"Block “{section.label}” saved.")
        return redirect("home_section_list")


class HomeSectionDeleteView(AdminRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        section = get_object_or_404(HomeSection, pk=pk)
        label = section.label
        self.log_action("Deleted home section", section)
        section.delete()
        messages.success(request, f"Block “{label}” deleted.")
        return redirect("home_section_list")
