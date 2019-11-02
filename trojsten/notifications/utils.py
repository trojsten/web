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

    for user in users:
        if user.pk in unsubscribed:
            continue

        Notification.objects.create(user=user, channel=channel, message=message, url=url)
