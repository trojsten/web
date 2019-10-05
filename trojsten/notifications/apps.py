from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = "trojsten.notifications"

    def ready(self):
        # This is here to register events.
        # See https://docs.djangoproject.com/en/2.2/topics/signals/#connecting-receiver-functions
        # For more information.
        import trojsten.notifications.signals.submit  # noqa
        import trojsten.notifications.signals.contest  # noqa
