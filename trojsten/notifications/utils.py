from .models import Notification, UnsubscribedChannel


def notify(users, channel, message, url):
    """
    Notifies all users in `users` that are not unsubscribed.

    Arguments:
    users -- iterable containing instances of trojsten.people.models.User
    channel -- notification channel name
    message -- display message for user
    url -- URL to open when read
    """

    unsubscribed = UnsubscribedChannel.objects.filter(channel=channel).values_list(
        "user__pk", flat=True
    )

    notifications = []

    for user in users:
        if user.pk in unsubscribed:
            continue

        notifications.append(Notification(user=user, channel=channel, message=message, url=url))

    # @TODO: Use Celery to create notifications asynchronously
    Notification.objects.bulk_create(notifications)


def notify_user(user, channel, message, url):
    """
    Notifies a single user.

    See notify().
    """
    notify([user], channel, message, url)
