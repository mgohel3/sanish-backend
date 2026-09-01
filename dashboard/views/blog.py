from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from accounts.permissions import ContentManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from blog.models import BlogPost, BlogCategory, Tag


class BlogPostListView(ContentManagerRequiredMixin, View):
    def get(self, request):
        qs = BlogPost.objects.select_related("author").order_by("-created")
        q  = request.GET.get("q", "")
        status = request.GET.get("status", "")
        if q:
            qs = qs.filter(title__icontains=q)
        if status:
            qs = qs.filter(status=status)
        return render(request, "dashboard/blog/list.html", {
            "posts":      qs,
            "q": q, "selected_status": status,
            "active_nav": "blog",
        })


class BlogPostCreateView(ContentManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/blog/form.html", {
            "categories": BlogCategory.objects.all(),
            "tags":       Tag.objects.all(),
            "active_nav": "blog",
        })

    def post(self, request):
        d = request.POST
        post = BlogPost(
            title=d["title"],
            content=d.get("content", ""),
            author=request.user,
            status=d.get("status", "draft"),
            seo_title=d.get("seo_title", ""),
            meta_description=d.get("meta_description", ""),
            meta_keywords=d.get("meta_keywords", ""),
            auto_faq_schema=bool(d.get("auto_faq_schema")),
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
            "post":       post,
            "categories": BlogCategory.objects.all(),
            "tags":       Tag.objects.all(),
            "active_nav": "blog",
        })

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        d = request.POST
        post.title = d["title"]
        post.content = d.get("content", "")
        post.status = d.get("status", "draft")
        post.seo_title = d.get("seo_title", "")
        post.meta_description = d.get("meta_description", "")
        post.meta_keywords = d.get("meta_keywords", "")
        post.auto_faq_schema = bool(d.get("auto_faq_schema"))
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
