from django.apps import AppConfig


class TitlesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "titles"

    def ready(self) -> None:
        from . import signals
