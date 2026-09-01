from django.db import models


class Inquiry(models.Model):
    TYPE_CONTACT  = "contact"
    TYPE_DEALER   = "dealer"
    TYPE_ARCHITECT = "architect"
    TYPE_CHOICES  = [
        (TYPE_CONTACT,   "Contact"),
        (TYPE_DEALER,    "Dealer"),
        (TYPE_ARCHITECT, "Architect"),
    ]

    STATUS_NEW       = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_QUALIFIED = "qualified"
    STATUS_CLOSED    = "closed"
    STATUS_CHOICES   = [
        (STATUS_NEW,       "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_QUALIFIED, "Qualified"),
        (STATUS_CLOSED,    "Closed"),
    ]

    type        = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_CONTACT)
    name        = models.CharField(max_length=200)
    email       = models.EmailField()
    phone       = models.CharField(max_length=20, blank=True)
    message     = models.TextField(blank=True)
    city        = models.CharField(max_length=100, blank=True)
    source_page = models.CharField(max_length=500, blank=True)
    status      = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_NEW)
    notes       = models.TextField(blank=True, help_text="Internal follow-up notes")
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"{self.name} ({self.type}) — {self.status}"


class Dealer(models.Model):
    STATUS_ACTIVE   = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES  = [
        (STATUS_ACTIVE,   "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    name    = models.CharField(max_length=255)
    contact = models.CharField(max_length=200, blank=True)
    email   = models.EmailField(blank=True)
    phone   = models.CharField(max_length=20, blank=True)
    city    = models.CharField(max_length=100)
    state   = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    lat     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status  = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["city", "name"]

    def __str__(self):
        return f"{self.name}, {self.city}"
