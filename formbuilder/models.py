from django.db import models

# ─────────────────────────────────────────────────────────────────────────────
# Generic CMS-managed forms — any page can point at a ``FormDefinition`` by
# slug and get a form whose fields the client can add/remove/reorder from the
# CMS, without touching code. Deliberately separate from ``leads.Inquiry``
# (the fixed-field contact/dealer/architect pipeline that already exists and
# stays untouched) so this is purely additive.
# ─────────────────────────────────────────────────────────────────────────────

FIELD_TYPES = [
    ("text", "Text"),
    ("email", "Email"),
    ("tel", "Phone"),
    ("textarea", "Textarea"),
    ("number", "Number"),
    ("select", "Dropdown"),
    ("radio", "Radio buttons"),
    ("checkbox", "Checkbox"),
    ("hidden", "Hidden"),
]

FIELD_TYPES_WITH_OPTIONS = {"select", "radio"}


class FormDefinition(models.Model):
    """One CMS-editable form. Any number of pages/blocks can reference it by slug."""

    TARGET_SUBMISSION = "submission"
    TARGET_INQUIRY = "inquiry"
    TARGET_CHOICES = [
        (TARGET_SUBMISSION, "Generic submission (view under Forms → Submissions)"),
        (TARGET_INQUIRY, "Leads pipeline (view under Leads, same as the Contact form today)"),
    ]

    slug = models.SlugField(
        max_length=80, unique=True,
        help_text='Referenced by pages/blocks, e.g. "quote-request".',
    )
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    submit_label = models.CharField(max_length=60, default="Submit")
    success_message = models.CharField(
        max_length=255, default="Thank you! We'll be in touch shortly."
    )
    notify_emails = models.CharField(
        max_length=500, blank=True,
        help_text="Comma-separated emails notified on submission. Falls back to the site's default notify list.",
    )
    auto_reply_enabled = models.BooleanField(
        default=False,
        help_text="Send an automatic confirmation email back to the person who submitted this form.",
    )
    auto_reply_subject = models.CharField(
        max_length=200, blank=True, default="Thanks for contacting {{site_name}}",
    )
    auto_reply_body = models.TextField(
        blank=True,
        default=(
            "Hi {{name}},\n\n"
            "Thanks for reaching out to {{site_name}}. We've received your message "
            "and will get back to you shortly.\n\n"
            "— {{site_name}} Team"
        ),
        help_text="Supports {{name}}, {{email}}, {{site_name}}, and {{field_name}} for any of this form's own fields.",
    )
    webhook_enabled = models.BooleanField(
        default=False,
        help_text="POST every submission as JSON to an external URL — for CRMs, Zapier, Google Sheets, etc.",
    )
    webhook_url = models.URLField(
        max_length=500, blank=True,
        help_text="e.g. a Zapier/Make catch hook, or your CRM's inbound webhook endpoint.",
    )
    webhook_secret = models.CharField(
        max_length=200, blank=True,
        help_text="Optional. Sent as the X-Webhook-Secret header so the receiving end can verify the request came from us.",
    )
    target_pipeline = models.CharField(
        max_length=20, choices=TARGET_CHOICES, default=TARGET_SUBMISSION,
        help_text="Where a submission of this form is stored.",
    )
    inquiry_type = models.CharField(
        max_length=10, blank=True,
        help_text='Only used when Target is "Leads pipeline" — one of contact / dealer / architect. '
                   'Leave blank to default to "contact".',
    )
    is_system = models.BooleanField(
        default=False, help_text="System forms cannot be deleted from the CMS.",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Form"

    def __str__(self):
        return self.name

    def notify_email_list(self):
        return [e.strip() for e in self.notify_emails.split(",") if e.strip()]


class FormField(models.Model):
    """One orderable field on a :class:`FormDefinition`."""

    form = models.ForeignKey(FormDefinition, on_delete=models.CASCADE, related_name="fields")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default="text")
    name = models.SlugField(
        max_length=60, help_text='Machine key submitted in the payload, e.g. "phone".',
    )
    label = models.CharField(max_length=120)
    placeholder = models.CharField(max_length=150, blank=True)
    help_text = models.CharField(max_length=255, blank=True)
    required = models.BooleanField(default=False)
    options = models.JSONField(
        default=list, blank=True,
        help_text="For dropdown/radio fields — list of option labels.",
    )
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
        unique_together = ("form", "name")
        verbose_name = "Form Field"

    def __str__(self):
        return f"{self.form.slug} · {self.label}"


class FormSubmission(models.Model):
    """A visitor's submission of a :class:`FormDefinition`, stored as raw field data."""

    form = models.ForeignKey(FormDefinition, on_delete=models.CASCADE, related_name="submissions")
    data = models.JSONField(default=dict, blank=True)
    source_page = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Form Submission"

    def __str__(self):
        return f"{self.form.slug} submission #{self.pk}"
