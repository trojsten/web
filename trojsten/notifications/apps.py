from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'trojsten.notifications'

    def ready(self):
        import trojsten.notifications.signals