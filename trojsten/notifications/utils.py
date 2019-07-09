from django.contrib.contenttypes.models import ContentType
from django_nyt.models import Notification, NotificationType, Settings, Subscription
from django_nyt.utils import subscribe

from .models import IgnoredNotifications


def subscribe_user_auto(user, key, target=None, force=False):
    """
    Subscribe user to a `key` using automagical (default) settings.

    :param: user: User to subscribe
    :param: key: NotificationType key to subscribe to
    :param: target: Object to subscribe to
    :param: force: Wether to force subscription. (Ignores and removes any IgnoredNotifications)
    """
    content_type = (
        ContentType.objects.get_for_model(target) if target is not None else None
    )
    object_id = target.pk if target is not None else None

    queryset = IgnoredNotifications.objects.filter(
        user=user, notification_type_id=key, object_id=object_id
    )

    if queryset.exists():
        if not force:
            return
        else:
            queryset.delete()

    return subscribe(
        Settings.get_default_setting(user),
        key,
        content_type=content_type,
        object_id=object_id,
    )


def unsubscribe_user(user, key, target=None, ignore=True):
    """
    Unsubscribe user from `key`.

    :param: user: User to unsubscribe
    :param: key: NotificationType key to unsubscribe from
    :param: target: Object to unsubscribe from
    :param: ignore: Wether to add this to IgnoredNotifications. (Default behaviour)
    """
    content_type = (
        ContentType.objects.get_for_model(target) if target is not None else None
    )
    object_id = target.pk if target is not None else None

    notification_type = NotificationType.get_by_key(key, content_type=content_type)

    Subscription.objects.filter(
        settings__user=user, notification_type=notification_type, object_id=object_id
    ).delete()

    if ignore:
        return IgnoredNotifications.objects.get_or_create(
            user=user, notification_type=notification_type, object_id=object_id
        )[0]


def unsubscribe_user_subscription(subscription, ignore=True):
    """
    Unsubscribe user from `subscription`.

    :param: subscription: Subscription to unsubscribe
    :param: ignore: Wether to add this to IgnoredNotifications. (Default behaviour)
    """

    target = None
    if subscription.object_id:
        target = (
            subscription.notification_type.content_type.model_class()
            .objects.filter(pk=subscription.object_id)
            .get()
        )

    return unsubscribe_user(
        subscription.settings.user, subscription.notification_type.key, target, ignore
    )


def was_notification_sent(key, target=None):
    """
    Check if we already sent any notification with `key` and `target`.

    :param: key: NotificationType key.
    :param: target: Object of interest
    """
    content_type = (
        ContentType.objects.get_for_model(target) if target is not None else None
    )
    object_id = target.pk if target is not None else None

    notification_type = NotificationType.get_by_key(key, content_type=content_type)

    return Notification.objects.filter(
        subscription__notification_type=notification_type,
        subscription__object_id=object_id,
    ).exists()
