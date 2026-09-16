from django.apps import AppConfig


class FormbuilderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "formbuilder"
    verbose_name = "Form Builder"

    def ready(self):
        from . import signals  # noqa: F401
