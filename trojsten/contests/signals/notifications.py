from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from trojsten.contests.models import Round, Task
from trojsten.notifications.utils import notify, notify_user
from trojsten.people.constants import SCHOOL_YEAR_END_MONTH
from trojsten.people.models import User
from trojsten.submit.constants import SUBMIT_STATUS_REVIEWED, SUBMIT_TYPE_DESCRIPTION
from trojsten.submit.models import Submit


@receiver(post_save, sender=Round, dispatch_uid="notifications__contest_publish")
def round_published(sender, **kwargs):
    round = kwargs["instance"]

    if not round.visible or round.previous_visible:
        return

    date = timezone.now()
    current_year = date.year + int(date.month > SCHOOL_YEAR_END_MONTH)
    users = User.objects.filter(graduation__gte=current_year).exclude(
        ignored_competitions=round.semester.competition
    )

    site = Site.objects.get_current()
    url = "//%(domain)s%(url)s" % {
        "domain": site.domain,
        "url": reverse("task_list", args=(round.pk,)),
    }

    notify(users, "round_started", _("Round %(round)s has started!") % {"round": round}, url)


@receiver(post_save, sender=Task, dispatch_uid="notifications__task_points_visibility_changed")
def task_description_points_visibility_change(sender, **kwargs):
    task = kwargs["instance"]

    if not task.description_points_visible or task.last_saved_description_points_visible:
        return

    site = Site.objects.get_current()

    # Get latest submit for every user.
    submits = (
        Submit.objects.filter(
            submit_type=SUBMIT_TYPE_DESCRIPTION, task=task, testing_status=SUBMIT_STATUS_REVIEWED
        )
        .select_related("user")
        .order_by("user_id", "-time")
        .distinct("user_id")
    )

    for submit in submits:
        url = "//%(domain)s%(url)s" % {
            "domain": site.domain,
            "url": reverse("task_list", args=(task.pk,)),
        }

        notify_user(
            submit.user,
            "submit_reviewed",
            _('Your description for "%(task)s" has been reviewed. You earned %(points)d points!')
            % {"task": task, "points": submit.points},
            url,
        )
