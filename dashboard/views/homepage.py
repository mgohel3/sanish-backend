"""
Home Page block manager — reorder, enable/disable, edit and add the blocks that
make up the public home page. Content is stored on ``HomeSection.content`` (JSON)
and shaped by ``homepage.blocks.BLOCK_TYPES``.
"""
import re
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

# Every block gets these on top of its own declared fields — a shared
# background (colour, and/or image with a colour overlay) editors can set on
# any section without each block type having to declare it itself. Rendered
# by dashboard/partials/_background_fields.html and read generically here
# because they live outside ``BLOCK_TYPES[...]["fields"]``.
BACKGROUND_FIELDS = [
    {"name": "bg_color", "type": "text"},
    {"name": "bg_image", "type": "image"},
    {"name": "bg_overlay_opacity", "type": "number"},
]

# Optional per-section text styling — same "available on every block, blank
# means use the theme default" convention as BACKGROUND_FIELDS above.
# Rendered by dashboard/partials/_text_style_fields.html; read generically
# here because, like the background fields, it lives outside each block
# type's own declared ``fields``. This same _parse_content() is imported and
# reused by dashboard/views/pages.py, so these fields are available on every
# block in BOTH the Home Page builder and the Pages builder (About Us, etc)
# uniformly. Not every block's frontend component applies them yet — see
# src/lib/textStyle.ts and its call sites (SpecialEdition.tsx, TeamBlock.tsx)
# — but the field is safe to leave set for any block since an unwired block
# just ignores it (same "field it's not wired into yet" behaviour that was
# already true for BACKGROUND_FIELDS before most blocks read bg_color).
TEXT_STYLE_FIELDS = [
    {"name": "text_color", "type": "text"},
    {"name": "heading_font", "type": "text"},
    {"name": "heading_size", "type": "text"},
]


_STYLE_FONTS = {"sans", "serif", "Playfair Display", "Cormorant Garamond", "Lora", "Merriweather",
                "Poppins", "Montserrat", "Roboto", "Open Sans", "Oswald", "Dancing Script"}
_STYLE_SIZES = {"sm", "lg", "xl"}
_STYLE_ALIGN = {"left", "center", "right"}
_HEX_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")


def _clean_field_style(raw):
    """Validate one ``<field>__style`` JSON blob from the dashboard's field toolbar."""
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    out = {}
    if isinstance(data.get("color"), str) and _HEX_RE.match(data["color"]):
        out["color"] = data["color"]
    if data.get("font") in _STYLE_FONTS:
        out["font"] = data["font"]
    size = str(data.get("size", ""))
    if size in _STYLE_SIZES or (size.isdigit() and 8 <= int(size) <= 160):
        out["size"] = size
    if data.get("align") in _STYLE_ALIGN:
        out["align"] = data["align"]
    if data.get("bold") is True:
        out["bold"] = True
    if data.get("italic") is True:
        out["italic"] = True
    if data.get("underline") is True:
        out["underline"] = True
    return out


def _parse_content(block_type, post):
    """Turn a submitted form into a ``content`` dict for the given block type."""
    cfg = blocks.BLOCK_TYPES.get(block_type, {})
    content = {}
    for field in list(cfg.get("fields", [])) + BACKGROUND_FIELDS + TEXT_STYLE_FIELDS:
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
    # Per-field text styles from the field toolbar (blank = theme default).
    field_styles = {}
    for field in cfg.get("fields", []):
        if field["type"] in ("text", "textarea"):
            st = _clean_field_style(post.get(f"{field['name']}__style", ""))
            if st:
                field_styles[field["name"]] = st
    content["field_styles"] = field_styles
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
            "config": blocks.with_dynamic_options(cfg),
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
            "config": blocks.with_dynamic_options(section.block_config),
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
