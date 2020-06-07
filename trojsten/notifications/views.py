from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.decorators.http import require_POST

from .models import Notification
from .settings import CHANNELS


@login_required
def get_notifications(request):
    notifications = (
        Notification.objects.filter(user=request.user, was_read=False)
        .order_by("-created_at")
        .all()[:10]
    )

    icons = {}
    for channel in CHANNELS:
        icons[channel["key"]] = channel["icon"]

    serialized = []
    for notification in notifications:
        serialized.append(
            {
                "id": notification.pk,
                "channel": notification.channel,
                "message": notification.message,
                "url": reverse("notification_view", args=(notification.pk,)),
                "was_read": notification.was_read,
                "created_at": notification.created_at,
            }
        )

    return JsonResponse({"icons": icons, "notifications": serialized, "unread": len(notifications)})


@login_required
def read_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)

    if notification.user != request.user:
        return HttpResponseForbidden()

    notification.was_read = True
    notification.save()

    return redirect(notification.url)


@login_required
@require_POST
def read_all_notifications(request):
    Notification.objects.filter(user=request.user, was_read=False).update(was_read=True)
    return JsonResponse({"ok": True})
