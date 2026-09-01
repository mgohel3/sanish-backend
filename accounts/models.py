from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_SUPER_ADMIN    = "super_admin"
    ROLE_ADMIN          = "admin"
    ROLE_SEO_MANAGER    = "seo_manager"
    ROLE_CONTENT_MANAGER = "content_manager"
    ROLE_SALES_MANAGER  = "sales_manager"

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN,     "Super Admin"),
        (ROLE_ADMIN,           "Admin"),
        (ROLE_SEO_MANAGER,     "SEO Manager"),
        (ROLE_CONTENT_MANAGER, "Content Manager"),
        (ROLE_SALES_MANAGER,   "Sales Manager"),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=ROLE_CONTENT_MANAGER
    )
    avatar = models.ForeignKey(
        "media_library.MediaAsset",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="user_avatar",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_super_admin(self):
        return self.role == self.ROLE_SUPER_ADMIN

    @property
    def is_admin_or_above(self):
        return self.role in (self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN)

    @property
    def can_manage_seo(self):
        return self.role in (self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_SEO_MANAGER)

    @property
    def can_manage_content(self):
        return self.role in (
            self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN,
            self.ROLE_SEO_MANAGER, self.ROLE_CONTENT_MANAGER,
        )

    @property
    def can_manage_leads(self):
        return self.role in (
            self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_SALES_MANAGER
        )


class ActivityLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=255)
    object_repr = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Activity Log"

    def __str__(self):
        return f"{self.user} — {self.action} at {self.timestamp:%Y-%m-%d %H:%M}"

    @classmethod
    def log(cls, user, action, obj=None, request=None):
        ip = None
        if request:
            ip = (
                request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
                or request.META.get("REMOTE_ADDR")
            )
        cls.objects.create(
            user=user,
            action=action,
            object_repr=str(obj) if obj else "",
            ip=ip,
        )
