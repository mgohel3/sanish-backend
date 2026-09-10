import csv
import io
import json
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from django.utils.text import slugify

PRODUCTS_PER_PAGE = 20

import openpyxl

from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from catalog.models import (
    Product, Category, Collection, ProductImage,
    DESIGN_TYPE_CHOICES, COLOR_CHOICES, BADGE_CHOICES,
)
from media_library.models import MediaAsset

_ATTR_CHOICES = {
    "design_type_choices": [c[0] for c in DESIGN_TYPE_CHOICES],
    "color_choices":       [c[0] for c in COLOR_CHOICES],
    "badge_choices":       [c[0] for c in BADGE_CHOICES if c[0]],
}


class ProductListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        qs = Product.objects.select_related("category").order_by("-created")
        q  = request.GET.get("q", "")
        cat = request.GET.get("category", "")
        status = request.GET.get("status", "")
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(sku__icontains=q)
        if cat:
            qs = qs.filter(category_id=cat)
        if status:
            qs = qs.filter(status=status)

        total_count = qs.count()
        paginator = Paginator(qs, PRODUCTS_PER_PAGE)
        page_obj = paginator.get_page(request.GET.get("page"))
        elided_pages = list(paginator.get_elided_page_range(
            page_obj.number, on_each_side=2, on_ends=1
        ))

        querystring = request.GET.copy()
        querystring.pop("page", None)

        return render(request, "dashboard/products/list.html", {
            "products":    page_obj,
            "page_obj":    page_obj,
            "paginator":   paginator,
            "elided_pages": elided_pages,
            "total_count": total_count,
            "querystring": querystring.urlencode(),
            "categories":  Category.objects.all(),
            "q": q, "selected_cat": cat, "selected_status": status,
            "active_nav": "products",
        })


class ProductCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/products/form.html", {
            "categories":  Category.objects.filter(status="published"),
            "collections": Collection.objects.filter(status="published"),
            "all_products": Product.objects.all(),
            "active_nav": "products",
            **_ATTR_CHOICES,
        })

    def post(self, request):
        data = request.POST
        product = Product(
            name=data["name"],
            sku=data["sku"],
            category_id=data["category"],
            collection_id=data.get("collection") or None,
            short_description=data.get("short_description", ""),
            description=data.get("description", ""),
            features=json.loads(data.get("features_json", "[]")),
            tech_specs=json.loads(data.get("specs_json", "{}")),
            image_urls=json.loads(data.get("image_urls_json", "[]")),
            finish=data.get("finish", ""),
            thickness=data.get("thickness", ""),
            dimensions=data.get("dimensions", ""),
            surface=data.get("surface", ""),
            application=data.get("application", ""),
            design_type=data.get("design_type", ""),
            color=data.get("color", ""),
            badge=data.get("badge", ""),
            accent_color=data.get("accent_color", "") or "#85addc",
            meta_title=data.get("meta_title", ""),
            meta_description=data.get("meta_description", ""),
            meta_keywords=data.get("meta_keywords", ""),
            status=data.get("status", "draft"),
        )
        product.save()
        # Handle images — filter out blank strings
        image_ids = [i for i in request.POST.getlist("image_ids") if i.strip()]
        for pos, asset_id in enumerate(image_ids):
            try:
                asset = MediaAsset.objects.get(pk=int(asset_id))
                ProductImage.objects.create(product=product, asset=asset, position=pos)
            except (MediaAsset.DoesNotExist, ValueError, TypeError):
                pass
        # Related products — filter out blank strings
        rel_ids = [r for r in request.POST.getlist("related_products") if r.strip()]
        if rel_ids:
            product.related_products.set(rel_ids)
        self.log_action("Created product", product)
        messages.success(request, f"Product '{product.name}' created.")
        return redirect("product_edit", pk=product.pk)


class ProductEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, "dashboard/products/form.html", {
            "product":     product,
            "categories":  Category.objects.filter(status="published"),
            "collections": Collection.objects.filter(status="published"),
            "all_products": Product.objects.exclude(pk=pk),
            "current_images": product.product_images.select_related("asset").all(),
            "active_nav": "products",
            **_ATTR_CHOICES,
        })

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        data = request.POST
        product.name              = data["name"]
        product.sku               = data["sku"]
        product.category_id       = data["category"]
        product.collection_id     = data.get("collection") or None
        product.short_description = data.get("short_description", "")
        product.description       = data.get("description", "")
        product.features       = json.loads(data.get("features_json", "[]"))
        product.tech_specs     = json.loads(data.get("specs_json", "{}"))
        product.image_urls     = json.loads(data.get("image_urls_json", "[]"))
        product.finish         = data.get("finish", "")
        product.thickness      = data.get("thickness", "")
        product.dimensions     = data.get("dimensions", "")
        product.surface        = data.get("surface", "")
        product.application    = data.get("application", "")
        product.design_type    = data.get("design_type", "")
        product.color          = data.get("color", "")
        product.badge          = data.get("badge", "")
        product.accent_color   = data.get("accent_color", "") or "#85addc"
        product.meta_title     = data.get("meta_title", "")
        product.meta_description = data.get("meta_description", "")
        product.meta_keywords  = data.get("meta_keywords", "")
        product.status         = data.get("status", "draft")
        product.save()
        # Rebuild images — filter out blank strings before querying
        product.product_images.all().delete()
        image_ids = [i for i in request.POST.getlist("image_ids") if i.strip()]
        for pos, asset_id in enumerate(image_ids):
            try:
                asset = MediaAsset.objects.get(pk=int(asset_id))
                ProductImage.objects.create(product=product, asset=asset, position=pos)
            except (MediaAsset.DoesNotExist, ValueError, TypeError):
                pass
        # Related products — filter out blank strings
        rel_ids = [r for r in request.POST.getlist("related_products") if r.strip()]
        product.related_products.set(rel_ids)
        self.log_action("Updated product", product)
        messages.success(request, "Product updated.")
        return redirect("product_edit", pk=product.pk)


class ProductDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        self.log_action("Deleted product", product)
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect("product_list")


class ProductPreviewView(ContentManagerRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, "dashboard/preview/product.html", {
            "product":        product,
            "preview_title":  product.name,
            "preview_status": product.status,
            "edit_url":       f"/cms/products/{pk}/",
        })


# ── Bulk Export / Import (WooCommerce-style CSV) ──────────────────────────────

# Column order used for both export and the import template. `id` is optional on
# import (used to match an existing row); `sku` is the primary match key.
EXPORT_COLUMNS = [
    "id", "sku", "name", "slug", "status",
    "category", "collection",
    "short_description", "description",
    "features", "tech_specs",
    "finish", "thickness", "dimensions", "surface", "application",
    "design_type", "color", "badge", "accent_color",
    "image_urls",
    "meta_title", "meta_description", "meta_keywords",
]

# Multi-value cells are separated by " | ".
_LIST_SEP = " | "


def _join_list(values):
    return _LIST_SEP.join(str(v).strip() for v in (values or []) if str(v).strip())


def _split_list(raw):
    if raw is None:
        return []
    return [p.strip() for p in str(raw).split("|") if p.strip()]


def _specs_to_cell(specs):
    """dict -> 'Key: value | Key: value'."""
    if not isinstance(specs, dict):
        return ""
    return _LIST_SEP.join(f"{k}: {v}" for k, v in specs.items())


def _cell_to_specs(raw):
    """'Key: value | Key: value' -> dict (order preserved)."""
    out = {}
    for part in _split_list(raw):
        if ":" in part:
            k, v = part.split(":", 1)
            k = k.strip()
            if k:
                out[k] = v.strip()
    return out


def _product_to_row(p):
    return {
        "id":                p.pk,
        "sku":               p.sku,
        "name":              p.name,
        "slug":              p.slug,
        "status":            p.status,
        "category":          p.category.slug if p.category_id else "",
        "collection":        p.collection.slug if p.collection_id else "",
        "short_description": p.short_description,
        "description":       p.description,
        "features":          _join_list(p.features),
        "tech_specs":        _specs_to_cell(p.tech_specs),
        "finish":            p.finish,
        "thickness":         p.thickness,
        "dimensions":        p.dimensions,
        "surface":           p.surface,
        "application":       p.application,
        "design_type":       p.design_type,
        "color":             p.color,
        "badge":             p.badge,
        "accent_color":      p.accent_color,
        "image_urls":        _join_list(p.image_urls),
        "meta_title":        p.meta_title,
        "meta_description":  p.meta_description,
        "meta_keywords":     p.meta_keywords,
    }


def _parse_rows(file_obj, filename):
    """Parse an uploaded CSV or XLSX file into a list of dicts."""
    if filename.lower().endswith(".xlsx"):
        wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
        ws = wb.active
        headers = [str(c.value).strip() if c.value is not None else ""
                   for c in next(ws.iter_rows(min_row=1, max_row=1))]
        rows = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if all(v is None or str(v).strip() == "" for v in row):
                continue
            rows.append({h: ("" if v is None else str(v)) for h, v in zip(headers, row)})
        return rows
    text = file_obj.read().decode("utf-8-sig")
    return [dict(r) for r in csv.DictReader(io.StringIO(text))]


_DESIGN_TYPES = {c[0].lower(): c[0] for c in DESIGN_TYPE_CHOICES}
_COLORS       = {c[0].lower(): c[0] for c in COLOR_CHOICES}
_BADGES       = {c[0].lower(): c[0] for c in BADGE_CHOICES if c[0]}


class ProductExportView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    """Download all (or the currently-filtered) products as a CSV."""

    def get(self, request):
        qs = Product.objects.select_related("category", "collection").order_by("sku")
        q      = request.GET.get("q", "")
        cat    = request.GET.get("category", "")
        status = request.GET.get("status", "")
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(sku__icontains=q)
        if cat:
            qs = qs.filter(category_id=cat)
        if status:
            qs = qs.filter(status=status)

        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="products-export.csv"'
        writer = csv.DictWriter(resp, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        count = 0
        for p in qs:
            writer.writerow(_product_to_row(p))
            count += 1
        self.log_action(f"Exported {count} product(s) to CSV")
        return resp


class ProductImportView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    template_name = "dashboard/products/bulk_import.html"

    def get(self, request):
        return render(request, self.template_name, {"active_nav": "products"})

    def post(self, request):
        action = request.POST.get("action", "preview")

        if action == "download_template":
            return self._download_template()

        create_missing = request.POST.get("create_missing_categories") == "on"

        if action == "commit":
            raw_rows = json.loads(request.POST.get("raw_rows", "[]"))
            create_missing = request.POST.get("create_missing_flag") == "1"
            created = updated = skipped = 0
            with transaction.atomic():
                for row in raw_rows:
                    result = self._apply_row(row, create_missing)
                    if result == "created":
                        created += 1
                    elif result == "updated":
                        updated += 1
                    else:
                        skipped += 1
            self.log_action(
                f"Bulk import: {created} created, {updated} updated, {skipped} skipped"
            )
            messages.success(
                request,
                f"Import complete — {created} created, {updated} updated, {skipped} skipped.",
            )
            return redirect("product_list")

        # action == "preview"
        uploaded = request.FILES.get("import_file")
        if not uploaded:
            messages.error(request, "No file uploaded.")
            return redirect("product_import")
        try:
            rows = _parse_rows(uploaded, uploaded.name)
        except Exception as exc:  # noqa: BLE001 — surface any parse failure to the user
            messages.error(request, f"Could not read file: {exc}")
            return redirect("product_import")

        preview_rows = []
        error_count = 0
        for i, row in enumerate(rows, start=2):
            info = self._validate_row(row, create_missing)
            info["row"] = i
            preview_rows.append(info)
            if info["errors"]:
                error_count += 1

        return render(request, self.template_name, {
            "preview_rows":   preview_rows,
            "error_count":    error_count,
            "ready_count":    len(preview_rows) - error_count,
            "raw_rows":       json.dumps(rows),
            "create_missing": create_missing,
            "active_nav":     "products",
        })

    # ── helpers ──────────────────────────────────────────────────────────────

    def _resolve_category(self, name, create_missing):
        key = (name or "").strip()
        if not key:
            return None, "Missing category"
        cat = (Category.objects.filter(slug__iexact=key).first()
               or Category.objects.filter(name__iexact=key).first())
        if cat:
            return cat, None
        if create_missing:
            return Category.objects.create(
                name=key, slug=slugify(key), status=Category.STATUS_PUBLISHED
            ), None
        return None, f"Unknown category '{key}'"

    def _resolve_collection(self, name):
        key = (name or "").strip()
        if not key:
            return None, None
        col = (Collection.objects.filter(slug__iexact=key).first()
               or Collection.objects.filter(name__iexact=key).first())
        if col:
            return col, None
        return None, f"Unknown collection '{key}'"

    def _validate_row(self, row, create_missing):
        errors = []
        sku = (row.get("sku") or "").strip()
        name = (row.get("name") or "").strip()
        raw_id = (str(row.get("id") or "")).strip()

        existing = None
        if raw_id.isdigit():
            existing = Product.objects.filter(pk=int(raw_id)).first()
            if not existing:
                errors.append(f"No product with id {raw_id}")
        if not existing and sku:
            existing = Product.objects.filter(sku__iexact=sku).first()

        if not sku:
            errors.append("Missing sku")
        if not existing and not name:
            errors.append("Missing name (required for new products)")

        cat_val = (row.get("category") or "").strip()
        if cat_val or not existing:
            _, cat_err = self._resolve_category(cat_val, create_missing)
            # When updating an existing row a blank category keeps the current one.
            if cat_err and (cat_val or not existing):
                errors.append(cat_err)

        _, col_err = self._resolve_collection(row.get("collection"))
        if col_err:
            errors.append(col_err)

        for field, table in (("design_type", _DESIGN_TYPES),
                             ("color", _COLORS), ("badge", _BADGES)):
            val = (row.get(field) or "").strip()
            if val and val.lower() not in table:
                errors.append(f"Invalid {field} '{val}'")

        status = (row.get("status") or "").strip().lower()
        if status and status not in ("draft", "published"):
            errors.append(f"Invalid status '{status}'")

        return {
            "sku":    sku,
            "name":   name or (existing.name if existing else ""),
            "action": "skip" if errors else ("update" if existing else "create"),
            "errors": errors,
        }

    def _apply_row(self, row, create_missing):
        info = self._validate_row(row, create_missing)
        if info["errors"]:
            return "skipped"

        sku = info["sku"]
        raw_id = (str(row.get("id") or "")).strip()
        product = None
        if raw_id.isdigit():
            product = Product.objects.filter(pk=int(raw_id)).first()
        if not product:
            product = Product.objects.filter(sku__iexact=sku).first()
        is_new = product is None
        if is_new:
            product = Product(sku=sku)

        def has(col):
            return col in row and str(row.get(col)).strip() != ""

        if has("name"):
            product.name = row["name"].strip()
        if has("sku"):
            product.sku = sku
        if has("slug"):
            product.slug = slugify(row["slug"].strip())
        elif is_new:
            product.slug = ""  # model.save() will generate

        cat_val = (row.get("category") or "").strip()
        if cat_val or is_new:
            cat, _ = self._resolve_category(cat_val, create_missing)
            if cat:
                product.category = cat
        if "collection" in row:
            col_val = (row.get("collection") or "").strip()
            if col_val:
                col, _ = self._resolve_collection(col_val)
                product.collection = col
            else:
                product.collection = None

        text_fields = [
            "short_description", "description", "finish", "thickness",
            "dimensions", "surface", "application", "accent_color",
            "meta_title", "meta_description", "meta_keywords",
        ]
        for f in text_fields:
            if f in row:
                setattr(product, f, (row.get(f) or "").strip())

        if has("design_type"):
            product.design_type = _DESIGN_TYPES[row["design_type"].strip().lower()]
        if has("color"):
            product.color = _COLORS[row["color"].strip().lower()]
        if has("badge"):
            product.badge = _BADGES[row["badge"].strip().lower()]
        if not product.accent_color:
            product.accent_color = "#85addc"

        if "features" in row:
            product.features = _split_list(row.get("features"))
        if "tech_specs" in row:
            product.tech_specs = _cell_to_specs(row.get("tech_specs"))
        if "image_urls" in row:
            product.image_urls = _split_list(row.get("image_urls"))

        if has("status"):
            product.status = row["status"].strip().lower()
        elif is_new and not product.status:
            product.status = "draft"

        try:
            with transaction.atomic():
                product.save()
        except IntegrityError:
            return "skipped"
        return "created" if is_new else "updated"

    def _download_template(self):
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="products-import-template.csv"'
        writer = csv.DictWriter(resp, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        writer.writerow({
            "id": "", "sku": "LAM-001", "name": "Sample Laminate",
            "slug": "", "status": "draft",
            "category": "laminates", "collection": "",
            "short_description": "One-line summary",
            "description": "<p>Full rich-text description</p>",
            "features": "Scratch resistant | Heat resistant | Anti-fingerprint",
            "tech_specs": "Thickness: 1.0mm | Warranty: 10 years",
            "finish": "High Gloss", "thickness": "1.0mm",
            "dimensions": "8ft x 4ft (2440 x 1220mm)",
            "surface": "Decorative Laminate",
            "application": "Cabinets, Wardrobes, Wall Panels",
            "design_type": "Wood", "color": "Brown", "badge": "New",
            "accent_color": "#85addc",
            "image_urls": "https://example.com/a.jpg | https://example.com/b.jpg",
            "meta_title": "Sample Laminate | Sanish",
            "meta_description": "Buy sample laminate…",
            "meta_keywords": "laminate, wood laminate",
        })
        return resp
