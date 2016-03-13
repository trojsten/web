# -*- coding: utf-8 -*-

from .representation import ResultsRequest


def get_results(generator_key, round, single_round=False):
    # @TODO check for frozen results
    return _generate_results(generator_key, round, single_round)


def _generate_results(key, round, single_round):
    rules = round.series.competition.rules
    generator = rules.get_results_generators()[key]
    previous_rows = None
    if not single_round:
        previous_round = rules.get_previous_round(round)
        if previous_round is not None:
            previous_rows = get_results(key, previous_round, single_round).iterrows()
    request = ResultsRequest(
        round=round, single_round=single_round, previous_rows=previous_rows
    )
    return generator.run(request)
