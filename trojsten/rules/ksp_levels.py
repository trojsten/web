# Calculates history of KSP levels.
# Supports updates with finished semester or camp.

from collections import defaultdict

from trojsten.contests.models import Round, Competition
from trojsten.events.models import Event
from trojsten.results.manager import get_results


# TODO: with levels stored in DB, the access methods could be implemented in models.py
def get_user_level_for_semester(user, semester):
    """Needed for access to a level of one user e.g. in task list view."""
    return 1


def get_users_levels_for_semester(users, semester):
    """Needed for results calculation -- use only few cache queries. """
    return defaultdict(lambda: 1)


SEMESTER = 0
CAMP = 1


def prepare_events():
    """
    Produces a list events sorted by their start dates as a list of tuples of two types:
    semester: (SEMESTER, semester id)
    camp: (CAMP, camp id, associated semester id)
    """
    semesters = Round.objects.filter(
        semester__competition__name='KSP'
    ).order_by(
        'semester', 'start_time', 'pk'
    ).distinct(
        'semester'
    ).values_list('start_time', 'semester')
    semesters = [(start, SEMESTER, id) for start, id in semesters]

    ksp_site_id = Competition.objects.get(name='KSP').sites.first().id

    camps = Event.objects.filter(
        type__is_camp=True
    ).filter(
        type__sites__in=[ksp_site_id]
    ).order_by(
        'start_time'
    ).values_list('start_time', 'pk')
    camps = [(start, CAMP, id) for start, id in camps]

    events = sorted(semesters + camps)

    final_events_format = []

    for i, e in enumerate(events):
        if e[1] == SEMESTER:
            final_events_format.append((SEMESTER, e[2]))
        else:
            # i-1: current semester, i-2: previous camp, i-3: previous semester
            associated_semester = None if i-3 < 0 else events[i-3][2]
            final_events_format.append((CAMP, e[2], associated_semester))

    return final_events_format


def process_semester(semester_pk):
    round = Round.objects.filter(semester=semester).order_by('number').last().pk
    results = [get_results(tag_key, round, single_round=False) for tag_key in ['1', '2', '3', '4']]
    # TODO


def recalculate_levels():
    events = prepare_events()
    # TODO
