from trojsten.regal.contests.models import Round


def get_latest_rounds_by_competition():
    rounds = Round.objects.filter(
        visible=True
    ).order_by(
        'series__competition', '-end_time'
    ).distinct('series__competition')
    return {r.series.competition: r for r in rounds}


def get_rounds_by_year():
    rounds = Round.objects.filter(visible=True).order_by('-series__year', '-number')
    rounds_dict = dict()
    for round in rounds:
        if not round.series.year in rounds_dict:
            rounds_dict[round.series.year] = list()
        rounds_dict[round.series.year].append(round)
    return rounds_dict
