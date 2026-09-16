"""Admin-only Help Center — an in-CMS, multi-page reference explaining what
every dashboard section does and how to use it. Content is authored as
Markdown in the separate cms-docs/ project and compiled into
dashboard/data/help_content.json by cms-docs/scripts/documentation/
sync_to_cms_help.py — nothing here parses Markdown at request time, this
module only loads and serves the pre-built JSON.

Internal reference only: every view here requires CMS login (AdminRequiredMixin)
and is never linked from the public site."""
import json
from pathlib import Path

from django.http import Http404
from django.shortcuts import render
from django.views import View

from accounts.permissions import AdminRequiredMixin

HELP_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "help_content.json"


def _load_help_data():
    # Re-read on every call rather than caching: this is a low-traffic, admin-only
    # reference page, so a fresh ~300KB JSON parse per request is negligible — and
    # it means re-running sync_to_cms_help.py takes effect immediately, without a
    # server restart (a JSON data file doesn't trigger Django's autoreloader).
    with open(HELP_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


class HelpIndexView(AdminRequiredMixin, View):
    def get(self, request):
        data = _load_help_data()
        return render(request, "dashboard/help/index.html", {
            "active_nav": "help",
            "groups": data["groups"],
            "landing_html": data["landing_html"],
        })


class HelpArticleView(AdminRequiredMixin, View):
    def get(self, request, slug):
        data = _load_help_data()
        article = data["articles"].get(slug)
        if not article:
            raise Http404("Help article not found")
        current_group = next((g for g in data["groups"] if g["id"] == article["group_id"]), None)
        return render(request, "dashboard/help/article.html", {
            "active_nav": "help",
            "groups": data["groups"],
            "article": article,
            "current_group": current_group,
        })
