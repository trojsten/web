from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect

from .models import Notification


@login_required
def get_notifications(request):
    notifications = (
        Notification.objects.filter(user=request.user)
        .order_by("-was_read", "-created_at")
        .select_related("subscription")
        .all()[:10]
    )

    serialized = []
    unread = 0

    for notification in notifications:
        serialized.append(
            {
                "id": notification.pk,
                "identificator": notification.subscription.notification_type,
                "message": notification.message,
                "was_read": notification.was_read,
                "created_at": notification.created_at,
            }
        )

        if not notification.was_read:
            unread += 1

    return JsonResponse({"notifications": serialized, "unread": unread})


@login_required
def read_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)

    if notification.user != request.user:
        return HttpResponseForbidden()

    notification.was_read = True
    notification.save()

    return redirect(notification.url)
