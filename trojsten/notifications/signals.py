from django.dispatch import receiver
from django.db.models.signals import post_save
from django_nyt.utils import notify
from django_nyt.models import Settings
from django.utils.translation import ugettext as _
from django.urls import reverse

from trojsten.submit.models import Submit
from trojsten.submit.constants import (SUBMIT_TYPE_DESCRIPTION, SUBMIT_STATUS_REVIEWED)
from trojsten.notifications import constants
from trojsten.notifications.utils import subscribe_user_auto

@receiver(post_save, sender=Submit)
def submit_saved(sender, **kwargs):
    instance = kwargs['instance']

    # Posielame notifikacie len pre popisy.
    if instance.submit_type != SUBMIT_TYPE_DESCRIPTION:
        return
    
    # Ak bol opraveny, napis o tom ucastnikovi.
    if instance.testing_status == SUBMIT_STATUS_REVIEWED:
        notify(
            _('Your description for "%(task)s" has been reviewed. You earned %(points)d points!') % {'task': instance.task, 'points': instance.points},
            constants.NOTIFICATION_SUBMIT_REVIEWED,
            target_object=instance.user,
            url=reverse("task_submit_page", args=(instance.task_id, ))
        )
    # Ak bol iba pridany, skontroluj, ci ucastnik subscribuje notifikacie a aplikuj jeho nastavenia.
    elif instance.testing_status == SUBMIT_STATUS_IN_QUEUE:
        subscribe_user_auto(instance.user, constants.NOTIFICATION_SUBMIT_REVIEWED, instance.user)