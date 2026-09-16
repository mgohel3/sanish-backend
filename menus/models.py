from django.db import models

# ─────────────────────────────────────────────────────────────────────────────
# A generic, hierarchical (WordPress-style) menu builder — any number of
# menus, each an ordered tree of links up to one level of nesting (dropdown
# submenus). This is the single CMS screen for all site navigation: the
# live Header, Top Bar, Mega Menu quick links, and Footer are each a
# non-deletable "system" menu (``Menu.is_system``) managed here, alongside
# any custom menus. Supersedes the old ``seo.NavLink`` model, whose table is
# kept only as historical data and is no longer read anywhere.
# ─────────────────────────────────────────────────────────────────────────────


class Menu(models.Model):
    slug = models.SlugField(
        max_length=60, unique=True,
        help_text='Referenced by the frontend, e.g. "footer-resources".',
    )
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    is_system = models.BooleanField(
        default=False, help_text="System menus cannot be deleted from the CMS.",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children",
        help_text="Leave blank for a top-level item; set to nest as a dropdown submenu item.",
    )
    label = models.CharField(max_length=80)
    url = models.CharField(
        max_length=300, blank=True,
        help_text="Relative (/about-us) or absolute URL. Leave blank for a label-only dropdown trigger.",
    )
    open_new_tab = models.BooleanField(default=False)
    position = models.PositiveSmallIntegerField(default=0, help_text="Lower = appears first among its siblings.")
    active = models.BooleanField(default=True, help_text="Inactive items are hidden from the live site without deleting them.")

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.menu.slug} · {self.label}"
