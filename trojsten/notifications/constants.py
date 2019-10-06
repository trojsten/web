from enum import IntEnum


class SubscriptionStatus(IntEnum):
    UNSUBSCRIBED = 0
    SUBSCRIBED = 1


STATUSES = [
    (SubscriptionStatus.UNSUBSCRIBED, "Unsubscribed"),
    (SubscriptionStatus.SUBSCRIBED, "Subscribed"),
]
