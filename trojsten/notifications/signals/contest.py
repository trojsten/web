from django.db.models.signals import post_save
from django.dispatch import receiver

from trojsten.contests.models import Round
from trojsten.notifications.notification_types import RoundStarted


@receiver(post_save, sender=Round, dispatch_uid="notifications__contest_publish")
def round_published(sender, **kwargs):
    instance = kwargs["instance"]

    if not instance.visible or instance.previous_visible:
        return

    RoundStarted(instance.semester.competition).dispatch({"round": instance})
