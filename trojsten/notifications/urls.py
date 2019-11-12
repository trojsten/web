from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_notifications, name="notification_list"),
    path("<int:notification_id>/", views.read_notification, name="notification_view"),
]
