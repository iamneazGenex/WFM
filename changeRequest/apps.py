from django.apps import AppConfig


class ChangerequestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "changeRequest"

    def ready(self):
        import changeRequest.signals
