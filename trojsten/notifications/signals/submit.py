from django.dispatch import receiver
from django.db.models.signals import post_save
from django_nyt.utils import notify
from django.utils.translation import ugettext as _
from django.urls import reverse

from trojsten.submit.models import Submit
from trojsten.submit.constants import (SUBMIT_TYPE_DESCRIPTION,
                                       SUBMIT_STATUS_REVIEWED,
                                       SUBMIT_STATUS_IN_QUEUE)
from trojsten.notifications import constants
from trojsten.notifications.utils import subscribe_user_auto


@receiver(post_save, sender=Submit, dispatch_uid="notifications_submit_review")
def submit_reviewed(sender, **kwargs):
    instance = kwargs['instance']

    # Posielame notifikacie len pre popisy.
    if instance.submit_type != SUBMIT_TYPE_DESCRIPTION:
        return

    # Ak bol opraveny, napis o tom ucastnikovi.
    if instance.testing_status == SUBMIT_STATUS_REVIEWED:
        text = _(
            'Your description for "%(task)s" has been reviewed. You earned %(points)d points!'
        ) % {
            'task': instance.task,
            'points': instance.points
        }

        notify(text,
               constants.NOTIFICATION_SUBMIT_REVIEWED,
               target_object=instance.user,
               url=reverse("task_submit_page", args=(instance.task_id, )))
    # Ak bol iba pridany, skontroluj, ci ucastnik subscribuje notifikacie a aplikuj jeho nastavenia.
    elif instance.testing_status == SUBMIT_STATUS_IN_QUEUE:
        subscribe_user_auto(instance.user,
                            constants.NOTIFICATION_SUBMIT_REVIEWED,
                            instance.user)


@receiver(post_save,
          sender=Submit,
          dispatch_uid="notifications_submit_created")
def submit_created(sender, **kwargs):
    """
    Subscribe user to future updates about a given contest after submitting.
    """
    instance = kwargs['instance']

    # Auto-subscribe len pre nove submity.
    if instance.testing_status != SUBMIT_STATUS_IN_QUEUE:
        return

    subscribe_user_auto(instance.user,
                        constants.NOTIFICATION_CONTEST_NEW_ROUND,
                        instance.task.round.semester.competition)
