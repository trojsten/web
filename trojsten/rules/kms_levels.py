# -*- coding: utf-8 -*-
# Calculates history of KMS levels.
# Supports updates with finished semester or camp.

import logging
from collections import namedtuple

from django.db.models import Q

from trojsten.contests.models import Round
from trojsten.events.models import Event, EventParticipant
from trojsten.people.models import User
from trojsten.results.helpers import get_total_score_column_index
from trojsten.results.manager import get_results
from trojsten.rules.models import KMSLevel

logger = logging.getLogger("management_commands")

KMS_CAMP_TYPE = "KMS sústredenie"
KMS_POINTS_FOR_SUCCESSFUL_LEVEL = {1: 84, 2: 84, 3: 84, 4: 93, 5: 93}

# Either a semester or a camp which will yield level-ups.
ResultsAffectingEvent = namedtuple(
    "ResultsAffectingEvent",
    "start_time, semester, camp, associated_semester, last_semester_before_level_up",
)


def prepare_events(latest_event_start_date):
    """Produces a list of all ResultsAffectingEvents sorted by their start dates."""
    last_rounds = (
        Round.objects.filter(
            semester__competition__name="KMS", start_time__lte=latest_event_start_date
        )
        .order_by("semester", "start_time", "pk")
        .distinct("semester")
        .select_related("semester")
    )

    semesters = []
    for last_round in last_rounds:
        semesters.append(
            ResultsAffectingEvent(
                start_time=last_round.start_time,
                semester=last_round.semester,
                camp=None,
                associated_semester=last_round.semester,
                last_semester_before_level_up=last_round.semester,
            )
        )

    camp_objects = (
        Event.objects.filter(
            type__is_camp=True,
            start_time__lte=latest_event_start_date,
            type__name=KMS_CAMP_TYPE,
        )
        .order_by("start_time")
        .select_related("semester")
    )

    camps = []
    for camp_object in camp_objects:
        camps.append(
            ResultsAffectingEvent(
                start_time=camp_object.start_time,
                semester=None,
                camp=camp_object,
                associated_semester=camp_object.semester,
                last_semester_before_level_up=camp_object.semester,
            )
        )

    return sorted(semesters + camps)


def level_updates_from_semester_results(semester, level_up_score_thresholds=None):
    """
    Returns a list of LevelUpRecords for users whose level should be updated.
    Competitors with at least 80 % of points from semester get a levelling boost (results_table_level + 1) for the
    next semester.

    Optionally define custom level-up thresholds for different result table levels by setting
    `level_up_score_thresholds`.
    """
    if level_up_score_thresholds is None:
        level_up_score_thresholds = KMS_POINTS_FOR_SUCCESSFUL_LEVEL

    round = Round.objects.filter(semester=semester).order_by("number").last()
    # TODO: Get frozen results table if available.
    result_tables = [
        (get_results("KMS_L{}".format(level), round, single_round=False), level)
        for level in range(1, 5)
    ]

    updates = []
    for table, table_level in result_tables:
        total_score_column_index = get_total_score_column_index(table)
        if total_score_column_index is None:
            logger.warning(
                'Results table {} for round {} does not contain "sum" column.'.format(
                    table.tag, table.round
                )
            )
            continue

        for row in table.serialized_results["rows"]:
            # Skip organizers and (hidden) participants with level higher than table level.
            if not row["active"]:
                continue
            total_points = float(row["cell_list"][total_score_column_index]["points"])
            if total_points < level_up_score_thresholds[table_level]:
                break
            try:
                level_up = KMSLevel(
                    user=User.objects.get(pk=row["user"]["id"]),
                    new_level=min(5, table_level + 1),
                    source_semester=semester,
                    last_semester_before_level_up=semester,
                )
                updates.append(level_up)
            except User.DoesNotExist:
                logger.warning("User with id {} does not exist.".format(row["user"]["id"]))

    return updates


def level_updates_from_camp_attendance(camp, associated_semester, last_semester_before_level_up):
    """
    Returns a list of LevelUpRecords for users whose level should be updated.
    All participants who attended the camp will receive a levelling boost (associated_semester_competitor_level + 1) for the next semester.
    """
    invited_users_pks = EventParticipant.objects.filter(
        Q(type=EventParticipant.PARTICIPANT) | Q(type=EventParticipant.RESERVE),
        event=camp,
        going=True,
    ).values_list("user__pk", flat=True)
    invited_users_pks_set = set(invited_users_pks)

    user_levels = KMSLevel.objects.for_users_in_semester_as_dict(
        associated_semester.pk, invited_users_pks
    )

    updates = list()
    for user_id in invited_users_pks_set:
        try:
            level_up = KMSLevel(
                user=User.objects.get(pk=user_id),
                new_level=min(5, user_levels[user_id] + 1),
                source_camp=camp,
                last_semester_before_level_up=last_semester_before_level_up,
            )
            updates.append(level_up)
        except User.DoesNotExist:
            logger.warning("User with id {} does not exist.".format(user_id))

    return updates
