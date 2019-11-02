from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from trojsten.notifications.utils import notify_user
from trojsten.submit.constants import SUBMIT_STATUS_REVIEWED, SUBMIT_TYPE_DESCRIPTION
from trojsten.submit.models import Submit


@receiver(post_save, sender=Submit, dispatch_uid="notifications__submit_review")
def submit_reviewed(sender, **kwargs):
    instance = kwargs["instance"]

    # We only send notifications related to descriptions.
    if instance.submit_type != SUBMIT_TYPE_DESCRIPTION:
        return

    # If this submit was reviewed, notify the user.
    if instance.testing_status == SUBMIT_STATUS_REVIEWED:
        site = Site.objects.get_current()
        url = "//%(domain)s%(url)s" % {
            "domain": site.domain,
            "url": reverse("task_submit_page", args=(instance.task.pk,)),
        }

        notify_user(
            instance.user,
            "submit_reviewed",
            _('Your description for "%(task)s" has been reviewed. You earned %(points)d points!')
            % {"task": instance.task, "points": instance.points},
            url,
        )
