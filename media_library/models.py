from django.db import models
from django.utils.text import slugify
from .utils import convert_to_webp


def asset_upload_path(instance, filename):
    folder = instance.folder.slug if instance.folder else "uncategorized"
    return f"media/{folder}/{filename}"


class MediaFolder(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="children",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MediaAsset(models.Model):
    TYPE_IMAGE = "image"
    TYPE_VIDEO = "video"
    TYPE_PDF   = "pdf"
    TYPE_OTHER = "other"

    TYPE_CHOICES = [
        (TYPE_IMAGE, "Image"),
        (TYPE_VIDEO, "Video"),
        (TYPE_PDF,   "PDF"),
        (TYPE_OTHER, "Other"),
    ]

    file = models.FileField(upload_to=asset_upload_path)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_IMAGE)
    folder = models.ForeignKey(
        MediaFolder, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="assets",
    )
    alt_text = models.CharField(max_length=300, blank=True)
    title = models.CharField(max_length=300, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    webp_version = models.FileField(
        upload_to="media/webp/", blank=True, null=True,
    )
    uploaded_by = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="uploaded_assets",
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Media Asset"

    def __str__(self):
        return self.title or self.file.name

    def save(self, *args, **kwargs):
        # Auto-detect type from extension
        if self.file:
            name = self.file.name.lower()
            if any(name.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")):
                self.type = self.TYPE_IMAGE
            elif any(name.endswith(ext) for ext in (".mp4", ".mov", ".avi", ".webm")):
                self.type = self.TYPE_VIDEO
            elif name.endswith(".pdf"):
                self.type = self.TYPE_PDF
        super().save(*args, **kwargs)
        # WebP conversion after first save (file is now persisted)
        if self.type == self.TYPE_IMAGE and not self.webp_version:
            try:
                webp_path = convert_to_webp(self)
                if webp_path:
                    MediaAsset.objects.filter(pk=self.pk).update(webp_version=webp_path)
                    self.webp_version = webp_path
            except Exception:
                pass

    @property
    def url(self):
        if self.webp_version:
            return self.webp_version.url
        return self.file.url if self.file else ""

    @property
    def original_url(self):
        return self.file.url if self.file else ""
