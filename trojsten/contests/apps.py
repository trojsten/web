from django.apps import AppConfig


class ContestsConfig(AppConfig):
    name = "trojsten.contests"

    def ready(self):
        # This is here to register events.
        # See https://docs.djangoproject.com/en/2.2/topics/signals/#connecting-receiver-functions
        # For more information.
        import trojsten.contests.signals.notifications  # noqa
