import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

OTP_VALID_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


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

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.get_full_name() or self.username

    def generate_otp(self):
        """Create a fresh 6-digit sign-in code, valid for OTP_VALID_MINUTES."""
        code = f"{secrets.randbelow(1_000_000):06d}"
        self.otp_code = code
        self.otp_expires_at = timezone.now() + timedelta(minutes=OTP_VALID_MINUTES)
        self.otp_attempts = 0
        self.save(update_fields=["otp_code", "otp_expires_at", "otp_attempts"])
        return code

    def verify_otp(self, code):
        """Check a submitted code. Returns True and clears the code on success."""
        if not self.otp_code or not self.otp_expires_at:
            return False
        if timezone.now() > self.otp_expires_at or self.otp_attempts >= OTP_MAX_ATTEMPTS:
            return False
        if not code or code != self.otp_code:
            self.otp_attempts += 1
            self.save(update_fields=["otp_attempts"])
            return False
        self.clear_otp()
        return True

    def clear_otp(self):
        self.otp_code = None
        self.otp_expires_at = None
        self.otp_attempts = 0
        self.save(update_fields=["otp_code", "otp_expires_at", "otp_attempts"])

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
