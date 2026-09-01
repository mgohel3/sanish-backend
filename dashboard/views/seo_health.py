from django.shortcuts import render
from django.db.models import Q
from django.views import View

from accounts.permissions import SEOManagerRequiredMixin
from catalog.models import Category, Collection, Product
from blog.models import BlogPost
from pages.models import CityPage


def _seo_score(obj, fields):
    """Return (score_0_to_100, list_of_missing_field_names)."""
    missing = [f for f in fields if not getattr(obj, f, None)]
    score = round((len(fields) - len(missing)) / len(fields) * 100)
    return score, missing


class SEOHealthView(SEOManagerRequiredMixin, View):
    # SEO fields we check per content type
    PRODUCT_FIELDS  = ["meta_title", "meta_description", "meta_keywords", "og_image"]
    CAT_FIELDS      = ["seo_title", "meta_description", "meta_keywords", "og_image"]
    BLOG_FIELDS     = ["seo_title", "meta_description", "meta_keywords", "og_image"]
    PAGE_FIELDS     = ["meta_title", "meta_description"]

    def get(self, request):
        ctx = self._build_context()
        ctx["active_nav"] = "seo"
        return render(request, "dashboard/seo/health.html", ctx)

    def _build_context(self):
        # ── Products ──────────────────────────────────────────────────────────
        products = list(Product.objects.filter(status="published").select_related("og_image"))
        product_issues = []
        product_total_score = 0
        for p in products:
            score, missing = _seo_score(p, self.PRODUCT_FIELDS)
            product_total_score += score
            if missing:
                product_issues.append({
                    "name": str(p),
                    "edit_url": f"/cms/products/{p.pk}/",
                    "score": score,
                    "missing": missing,
                })
        product_avg = round(product_total_score / len(products)) if products else 100
        product_issues.sort(key=lambda x: x["score"])

        # ── Categories ────────────────────────────────────────────────────────
        cats = list(Category.objects.filter(status="published").select_related("og_image"))
        cat_issues = []
        cat_total_score = 0
        for c in cats:
            score, missing = _seo_score(c, self.CAT_FIELDS)
            cat_total_score += score
            if missing:
                cat_issues.append({
                    "name": str(c),
                    "edit_url": f"/cms/categories/{c.pk}/",
                    "score": score,
                    "missing": missing,
                })
        cat_avg = round(cat_total_score / len(cats)) if cats else 100
        cat_issues.sort(key=lambda x: x["score"])

        # ── Collections ───────────────────────────────────────────────────────
        cols = list(Collection.objects.filter(status="published").select_related("og_image"))
        col_issues = []
        col_total_score = 0
        for c in cols:
            score, missing = _seo_score(c, self.CAT_FIELDS)
            col_total_score += score
            if missing:
                col_issues.append({
                    "name": str(c),
                    "edit_url": f"/cms/collections/{c.pk}/",
                    "score": score,
                    "missing": missing,
                })
        col_avg = round(col_total_score / len(cols)) if cols else 100

        # ── Blog Posts ────────────────────────────────────────────────────────
        posts = list(BlogPost.objects.filter(status="published").select_related("og_image"))
        blog_issues = []
        blog_total_score = 0
        for b in posts:
            score, missing = _seo_score(b, self.BLOG_FIELDS)
            blog_total_score += score
            if missing:
                blog_issues.append({
                    "name": str(b),
                    "edit_url": f"/cms/blog/{b.pk}/",
                    "score": score,
                    "missing": missing,
                })
        blog_avg = round(blog_total_score / len(posts)) if posts else 100
        blog_issues.sort(key=lambda x: x["score"])

        # ── City Pages ────────────────────────────────────────────────────────
        city_pages = list(CityPage.objects.filter(status="published"))
        city_missing_seo = [
            {"name": cp.city, "edit_url": f"/cms/city-pages/{cp.pk}/"}
            for cp in city_pages
            if not cp.seo_title and not cp.meta_description
        ]

        # ── Products missing images ───────────────────────────────────────────
        no_image_products = Product.objects.filter(
            status="published", product_images__isnull=True
        ).distinct()

        # ── Products missing description ──────────────────────────────────────
        no_desc_products = Product.objects.filter(
            status="published"
        ).filter(Q(description="") | Q(description__isnull=True))

        # Overall score
        all_scores = [product_avg, cat_avg, col_avg, blog_avg]
        overall = round(sum(all_scores) / len(all_scores))

        return {
            "overall":          overall,
            "scores": [
                ("Products",    product_avg, len(products)),
                ("Categories",  cat_avg,     len(cats)),
                ("Collections", col_avg,     len(cols)),
                ("Blog Posts",  blog_avg,    len(posts)),
            ],
            "product_avg":      product_avg,
            "product_total":    len(products),
            "product_issues":   product_issues[:20],
            "cat_avg":          cat_avg,
            "cat_total":        len(cats),
            "cat_issues":       cat_issues[:10],
            "col_avg":          col_avg,
            "col_total":        len(cols),
            "col_issues":       col_issues[:10],
            "blog_avg":         blog_avg,
            "blog_total":       len(posts),
            "blog_issues":      blog_issues[:10],
            "city_missing_seo": city_missing_seo[:10],
            "no_image_products":   no_image_products[:10],
            "no_desc_products":    no_desc_products[:10],
        }
