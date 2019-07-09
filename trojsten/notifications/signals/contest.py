from django.dispatch import receiver
from django.db.models.signals import post_save
from django_nyt.utils import notify
from django.utils.translation import ugettext as _
from django.urls import reverse

from trojsten.contests.models import Round
from trojsten.notifications import constants


@receiver(post_save,
          sender=Round,
          dispatch_uid="notifications_contest_publish")
def round_published(sender, **kwargs):
    instance = kwargs['instance']

    if not instance.visible or instance.previous_visible:
        return

    text = _("New round started! %(round)s") % {'round': instance}

    notify(text,
           constants.NOTIFICATION_CONTEST_NEW_ROUND,
           target_object=instance.semester.competition,
           url=reverse("task_list", args=(instance.pk, )))
