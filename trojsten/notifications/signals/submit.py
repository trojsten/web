from django.db.models.signals import post_save
from django.dispatch import receiver

from trojsten.notifications.notification_types import (RoundStarted,
                                                       SubmitReviewed)
from trojsten.submit.constants import (SUBMIT_STATUS_IN_QUEUE,
                                       SUBMIT_STATUS_REVIEWED,
                                       SUBMIT_TYPE_DESCRIPTION)
from trojsten.submit.models import Submit


@receiver(post_save, sender=Submit, dispatch_uid="notifications__submit_review")
def submit_reviewed(sender, **kwargs):
    instance = kwargs["instance"]

    # We only send notifications related to descriptions.
    if instance.submit_type != SUBMIT_TYPE_DESCRIPTION:
        return

    # If this submit was reviewed, notify the user.
    if instance.testing_status == SUBMIT_STATUS_REVIEWED:
        SubmitReviewed(instance.user).dispatch(
            {"task": instance.task, "points": instance.points}
        )
    # If was this submit only added to queue, subscribe the user to future notifications (related to the submit).
    elif instance.testing_status == SUBMIT_STATUS_IN_QUEUE:
        SubmitReviewed(instance.user).subscribe_unless_unsubscibed(instance.user)


@receiver(post_save, sender=Submit, dispatch_uid="notifications__submit_created")
def submit_created(sender, **kwargs):
    """
    Subscribe user to future updates about a given contest after submitting.
    """
    instance = kwargs["instance"]

    # We will only try to subscibe when a new submit is created.
    if instance.testing_status != SUBMIT_STATUS_IN_QUEUE:
        return

    RoundStarted(instance.task.round.semester.competition).subscribe_unless_unsubscibed(
        instance.user
    )
