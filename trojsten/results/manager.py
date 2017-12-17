# -*- coding: utf-8 -*-
from django.core.cache import cache

from .representation import ResultsRequest


class TagKeyError(Exception):
    pass


def get_results(tag_key, round, single_round):
    """
    Given a round and a results tag key returns the Results instance.

    The function abstracts the different result sources (generating, frozen, cached).
    """
    # FIXME(generic_results_stage_2): frozen results

    cache_key = '{}.{}.{}'.format(tag_key, round.pk, single_round)
    results = cache.get(cache_key)
    if results is None:
        results = _generate_results(tag_key, round, single_round)
        cache.set(cache_key, results)
    return results


def get_results_tags_for_rounds(rounds):
    """
    Returns generator of results tags coresponding to the `rounds`.

    Note that results tags may vary over time for the same competition.
    """
    # FIXME(generic_results_stage_2): frozen results
    # @FUTURE firstly try to get tags from frozen results and then calculate the rest
    return (
        r.semester.competition.rules.get_results_tags() for r in rounds
    )


def _generate_results(tag_key, round, single_round):
    rules = round.semester.competition.rules
    try:
        generator = rules.get_results_generator(tag_key)
    except KeyError:
        raise TagKeyError(tag_key)
    previous_rows = None
    if not single_round:
        previous_round = rules.get_previous_round(round)
        if previous_round is not None:
            previous_rows = get_results(tag_key, previous_round, single_round).iterrows()
    request = ResultsRequest(
        round=round, single_round=single_round, previous_rows=previous_rows,
    )
    return generator.run(request)
