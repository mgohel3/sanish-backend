from django.db import models

# ─────────────────────────────────────────────────────────────────────────────
# The site-wide FAQ page — a single CMS-managed list of question/answer pairs.
# Seeded from the FAQs already written into individual blog posts
# (``blog.BlogPost.faqs``), deduplicated onto one page so a visitor doesn't
# have to dig through articles to find an answer. ``source_post`` is kept for
# provenance / a "read more" link back to the originating article, but a FAQ
# entry can also be added directly here with no post behind it.
# ─────────────────────────────────────────────────────────────────────────────


class Faq(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField(help_text="Plain text or simple HTML (e.g. links) is fine.")
    source_post = models.ForeignKey(
        "blog.BlogPost", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="faq_entries",
        help_text="The blog post this FAQ was gathered from, if any.",
    )
    position = models.PositiveSmallIntegerField(default=0, help_text="Lower = appears first.")
    is_active = models.BooleanField(default=True, help_text="Inactive entries are hidden from the live site without deleting them.")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
