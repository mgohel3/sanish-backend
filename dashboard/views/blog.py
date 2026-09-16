import json

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from blog.models import BlogPost, BlogCategory, Tag

User = get_user_model()

BLOG_POSTS_PER_PAGE = 20

LAYOUT_VALUES = {c[0] for c in BlogPost.LAYOUT_CHOICES}


def _clean_layout(value):
    return value if value in LAYOUT_VALUES else BlogPost.LAYOUT_SIDEBAR


def _clean_faqs(raw_json):
    """Parse the FAQ repeater's hidden JSON field into a clean list of
    {question, answer} dicts, dropping any blank rows."""
    try:
        items = json.loads(raw_json or "[]")
    except (TypeError, ValueError):
        return []
    cleaned = []
    for item in items:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        if question and answer:
            cleaned.append({"question": question, "answer": answer})
    return cleaned


class BlogPostListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        qs = BlogPost.objects.select_related("author").order_by("-created")
        q  = request.GET.get("q", "")
        status = request.GET.get("status", "")
        if q:
            qs = qs.filter(title__icontains=q)
        if status:
            qs = qs.filter(status=status)

        total_count = qs.count()
        paginator = Paginator(qs, BLOG_POSTS_PER_PAGE)
        page_obj = paginator.get_page(request.GET.get("page"))
        elided_pages = list(paginator.get_elided_page_range(
            page_obj.number, on_each_side=2, on_ends=1
        ))

        querystring = request.GET.copy()
        querystring.pop("page", None)

        return render(request, "dashboard/blog/list.html", {
            "posts":       page_obj,
            "page_obj":    page_obj,
            "paginator":   paginator,
            "elided_pages": elided_pages,
            "total_count": total_count,
            "querystring": querystring.urlencode(),
            "q": q, "selected_status": status,
            "active_nav": "blog",
        })


class BlogPostCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/blog/form.html", {
            "categories":     BlogCategory.objects.all(),
            "tags":           Tag.objects.all(),
            "authors":        User.objects.filter(is_active=True).order_by("first_name", "username"),
            "layout_choices": BlogPost.LAYOUT_CHOICES,
            "active_nav":     "blog",
        })

    def post(self, request):
        d = request.POST
        author_id = d.get("author")
        post = BlogPost(
            title=d["title"],
            excerpt=d.get("excerpt", ""),
            content=d.get("content", ""),
            layout=_clean_layout(d.get("layout")),
            featured_image_url=d.get("featured_image_url", "").strip(),
            author=User.objects.filter(pk=author_id).first() if author_id else request.user,
            status=d.get("status", "draft"),
            seo_title=d.get("seo_title", ""),
            meta_description=d.get("meta_description", ""),
            meta_keywords=d.get("meta_keywords", ""),
            auto_faq_schema=bool(d.get("auto_faq_schema")),
            faqs=_clean_faqs(d.get("faqs_json")),
            show_author=bool(d.get("show_author")),
            show_share=bool(d.get("show_share")),
            show_related=bool(d.get("show_related")),
        )
        post.save()
        cat_ids = d.getlist("categories")
        if cat_ids:
            post.categories.set(cat_ids)
        tag_ids = d.getlist("tags")
        if tag_ids:
            post.tags.set(tag_ids)
        self.log_action("Created blog post", post)
        messages.success(request, "Blog post created.")
        return redirect("blog_post_edit", pk=post.pk)


class BlogPostEditView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        return render(request, "dashboard/blog/form.html", {
            "post":           post,
            "categories":     BlogCategory.objects.all(),
            "tags":           Tag.objects.all(),
            "authors":        User.objects.filter(is_active=True).order_by("first_name", "username"),
            "layout_choices": BlogPost.LAYOUT_CHOICES,
            "active_nav":     "blog",
        })

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        d = request.POST
        post.title = d["title"]
        post.excerpt = d.get("excerpt", "")
        post.content = d.get("content", "")
        post.layout = _clean_layout(d.get("layout"))
        post.featured_image_url = d.get("featured_image_url", "").strip()
        author_id = d.get("author")
        if author_id:
            post.author = User.objects.filter(pk=author_id).first()
        post.status = d.get("status", "draft")
        post.seo_title = d.get("seo_title", "")
        post.meta_description = d.get("meta_description", "")
        post.meta_keywords = d.get("meta_keywords", "")
        post.auto_faq_schema = bool(d.get("auto_faq_schema"))
        post.faqs = _clean_faqs(d.get("faqs_json"))
        post.show_author = bool(d.get("show_author"))
        post.show_share = bool(d.get("show_share"))
        post.show_related = bool(d.get("show_related"))
        post.save()
        post.categories.set(d.getlist("categories"))
        post.tags.set(d.getlist("tags"))
        self.log_action("Updated blog post", post)
        messages.success(request, "Blog post updated.")
        return redirect("blog_post_edit", pk=post.pk)


class BlogPostDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        self.log_action("Deleted blog post", post)
        post.delete()
        messages.success(request, "Blog post deleted.")
        return redirect("blog_list")


class BlogPostBulkDeleteView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def post(self, request):
        ids = [i for i in request.POST.getlist("ids") if i.strip().isdigit()]
        qs = BlogPost.objects.filter(pk__in=ids)
        count = qs.count()
        if count:
            titles = ", ".join(qs.values_list("title", flat=True)[:5])
            qs.delete()
            self.log_action(f"Bulk deleted {count} blog post(s): {titles}{'…' if count > 5 else ''}")
            messages.success(request, f"Deleted {count} post{'s' if count != 1 else ''}.")
        else:
            messages.error(request, "No posts selected.")
        return redirect("blog_list")


class BlogPostPreviewView(ContentManagerRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        return render(request, "dashboard/preview/blog_post.html", {
            "post":           post,
            "preview_title":  post.title,
            "preview_status": post.status,
            "edit_url":       f"/cms/blog/{pk}/",
        })


class BlogCategoryListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        return render(request, "dashboard/blog/categories.html", {
            "categories": BlogCategory.objects.all(),
            "tags":       Tag.objects.all(),
            "active_nav": "blog",
        })

    def post(self, request):
        action = request.POST.get("action", "")
        if action == "add_category":
            BlogCategory.objects.get_or_create(name=request.POST["name"])
            messages.success(request, "Category added.")
        elif action == "add_tag":
            Tag.objects.get_or_create(name=request.POST["name"])
            messages.success(request, "Tag added.")
        elif action == "delete_category":
            BlogCategory.objects.filter(pk=request.POST.get("id")).delete()
        elif action == "delete_tag":
            Tag.objects.filter(pk=request.POST.get("id")).delete()
        return redirect("blog_categories")
