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
    submit = kwargs["instance"]

    if (
        submit.submit_type != SUBMIT_TYPE_DESCRIPTION
        or submit.testing_status != SUBMIT_STATUS_REVIEWED
        or not submit.task.description_points_visible
    ):
        return

    site = Site.objects.get_current()
    url = "//%(domain)s%(url)s" % {
        "domain": site.domain,
        "url": reverse("task_submit_page", args=(submit.task.pk,)),
    }

    # If this submit was reviewed, notify the user.
    if kwargs["created"]:
        notify_user(
            submit.user,
            "submit_reviewed",
            _('Your description for "%(task)s" has been reviewed. You earned %(points)d points!')
            % {"task": submit.task, "points": submit.points},
            url,
        )
    # If we changed points, notify the user.
    elif submit.last_saved_points != submit.points:
        notify_user(
            submit.user,
            "submit_updated",
            _('Points for your description for "%(task)s" were updated to %(points)d points')
            % {"task": submit.task, "points": submit.points},
            url,
        )
