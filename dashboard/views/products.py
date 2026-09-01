import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from catalog.models import Product, Category, Collection, ProductImage
from media_library.models import MediaAsset


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
        return render(request, "dashboard/products/list.html", {
            "products":   qs,
            "categories": Category.objects.all(),
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
