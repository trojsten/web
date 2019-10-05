from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_notifications, name="list_notifications"),
    path("<int:notification_id>/", views.read_notification, name="read_notification"),
]
