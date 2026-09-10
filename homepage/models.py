from django.db import models

from . import blocks


class HomeSection(models.Model):
    """One orderable block on the public home page.

    ``content`` holds only the fields an editor has actually set; anything absent
    falls back to ``blocks.BLOCK_TYPES[block_type]['defaults']`` via ``resolved()``.
    """

    block_type = models.CharField(max_length=40, choices=blocks.block_choices())
    label      = models.CharField(
        max_length=120,
        help_text="Internal name shown in the CMS list (not published).",
    )
    anchor_id  = models.SlugField(
        max_length=60, blank=True,
        help_text='Optional id for the <section> tag (e.g. "about" → /#about).',
    )
    position   = models.PositiveIntegerField(default=0)
    enabled    = models.BooleanField(default=True)
    content    = models.JSONField(default=dict, blank=True)

    created    = models.DateTimeField(auto_now_add=True)
    updated    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Home Section"

    def __str__(self):
        return f"{self.position:02d}. {self.label} ({self.get_block_type_display()})"

    # ── helpers ────────────────────────────────────────────────────────────
    @property
    def block_config(self) -> dict:
        return blocks.BLOCK_TYPES.get(self.block_type, {})

    def resolved(self) -> dict:
        """Stored content merged over the block type's defaults."""
        data = blocks.defaults_for(self.block_type)
        if isinstance(self.content, dict):
            for key, value in self.content.items():
                if value in ("", None) and key in data:
                    continue  # keep the default rather than blanking it
                data[key] = value
        return data
