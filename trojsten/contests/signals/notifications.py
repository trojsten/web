from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from trojsten.contests.models import Round
from trojsten.notifications.utils import notify
from trojsten.people.constants import SCHOOL_YEAR_END_MONTH
from trojsten.people.models import User


@receiver(post_save, sender=Round, dispatch_uid="notifications__contest_publish")
def round_published(sender, **kwargs):
    instance = kwargs["instance"]

    if not instance.visible or instance.previous_visible:
        return

    date = timezone.now()
    current_year = date.year + int(date.month > SCHOOL_YEAR_END_MONTH)
    users = User.objects.filter(graduation__gte=current_year).exclude(
        ignored_competitions=instance.semester.competition
    )

    site = Site.objects.get_current()
    url = "//%(domain)s%(url)s" % {
        "domain": site.domain,
        "url": reverse("task_list", args=(instance.pk,)),
    }

    notify(users, "round_started", _("Round %(round)s has started!" % {"round": instance}), url)
