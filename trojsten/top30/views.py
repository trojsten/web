from django.db.models import Count
from django.shortcuts import render
from django.utils.translation import gettext as _

from trojsten.contests.constants import TASK_ROLE_REVIEWER
from trojsten.contests.models import Competition, TaskPeople
from trojsten.events.models import EventParticipant, EventType
from trojsten.people.models import User
from trojsten.submit.constants import SUBMIT_STATUS_REVIEWED, SUBMIT_TYPE_DESCRIPTION
from trojsten.submit.models import Submit

TOP_N = 30


def round_if_int(number):
    return round(number) if number == round(number) else number


def get_best(counts):
    return sorted(
        ((round_if_int(value), user.get_full_name()) for user, value in counts.items()),
        reverse=True,
    )[:TOP_N]


def get_reviewers(all_sites=False):
    query = Submit.objects.filter(
        submit_type=SUBMIT_TYPE_DESCRIPTION,
        testing_status=SUBMIT_STATUS_REVIEWED,
    )
    if not all_sites:
        competitions = Competition.objects.current_site_only()
        query = query.filter(task__round__semester__competition__in=competitions)
    submit_counts = query.values("task").annotate(submit_count=Count("task"))
    user_reviews = {}
    for submit_group in submit_counts:
        reviewers = [
            line.user
            for line in TaskPeople.objects.filter(
                task__id=submit_group["task"], role=TASK_ROLE_REVIEWER
            )
        ]
        for reviewer in reviewers:
            user_reviews[reviewer] = user_reviews.get(reviewer, 0) + submit_group[
                "submit_count"
            ] / len(reviewers)
    return get_best(user_reviews)


def get_camp_people(org, all_sites=False):
    roles = (
        [EventParticipant.ORGANIZER]
        if org
        else [EventParticipant.PARTICIPANT, EventParticipant.RESERVE]
    )
    query = EventParticipant.objects.filter(going=True, type__in=roles)
    if not all_sites:
        event_types = EventType.objects.current_site_only()
        query = query.filter(event__type__in=event_types)
    pariticipations = query.values("user").annotate(count=Count("user")).order_by("-count")[:TOP_N]
    return [
        (value["count"], User.objects.get(id=value["user"]).get_full_name())
        for value in pariticipations
    ]


def view_leaderboard(request):
    all_sites = request.GET.get("all_sites", False)
    return render(
        request,
        "trojsten/top30/top30.html",
        {
            "leaderboards": [
                (_("Most submissions reviewed"), get_reviewers(all_sites)),
                (_("Most camps organized"), get_camp_people(True, all_sites)),
                (_("Most camps attended"), get_camp_people(False)),
            ],
            "all_sites": all_sites,
        },
    )
