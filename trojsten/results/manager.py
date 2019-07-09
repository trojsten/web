# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.utils import timezone

from .models import Results
from .representation import ResultsRequest


class TagKeyError(Exception):
    pass


def get_results(tag_key, round, single_round):
    """
    Given a round and a results tag key returns the Results instance.

    The function abstracts the different result sources (generating, frozen, cached).
    """
    # FIXME(generic_results_stage_2): frozen results

    # TODO generate results async and use DB as cache
    cache_key = "{}.{}.{}".format(tag_key, round.pk, single_round)
    results = cache.get(cache_key)
    if results is None:
        try:
            results = Results.objects.get(round=round, tag=tag_key, is_single_round=single_round)
        except Results.DoesNotExist:
            pass
        if round.results_final:
            if not results:
                results = _generate_results(tag_key, round, single_round)
                results.save()
        else:
            results_pk = results.pk if results else None
            results = _generate_results(tag_key, round, single_round)
            results.pk = results_pk
            results.save()

        cache.set(cache_key, results)
    return results


def get_results_tags_for_rounds(rounds):
    """
    Returns generator of results tags coresponding to the `rounds`.

    Note that results tags may vary over time for the same competition.
    """
    # FIXME(generic_results_stage_2): frozen results
    # @FUTURE firstly try to get tags from frozen results and then calculate the rest
    return (r.semester.competition.rules.get_results_tags() for r in rounds)


def _generate_raw_results(tag_key, round, single_round):
    rules = round.semester.competition.rules
    try:
        generator = rules.get_results_generator(tag_key)
    except KeyError:
        raise TagKeyError(tag_key)
    previous_rows = None
    if not single_round:
        previous_round = rules.get_previous_round(round)
        if previous_round is not None:
            previous_rows = _generate_raw_results(tag_key, previous_round, single_round).iterrows()
    request = ResultsRequest(round=round, single_round=single_round, previous_rows=previous_rows)
    raw_results = generator.run(request)
    raw_results.calculate_cell_lists()

    return raw_results


def _generate_results(tag_key, round, single_round):
    raw_results = _generate_raw_results(tag_key, round, single_round)
    results = Results(
        round=round,
        tag=tag_key,
        is_single_round=single_round,
        has_previous_results=raw_results.has_previous,
        time=timezone.now(),
        serialized_results=raw_results.serialize(),
    )
    return results
