from __future__ import absolute_import

from django.db.models import Q

from trojsten.utils.permissions import set_permissions_from_filter


def is_competition_organizer_filter(user):
    if user.is_superuser:
        return None
    return Q(
        organizers_group__in=user.groups.all(),
    )


set_permissions_from_filter(
    'contests', 'competition', is_competition_organizer_filter,
)
