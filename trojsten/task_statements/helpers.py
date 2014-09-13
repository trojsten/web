from trojsten.regal.contests.models import Round


def get_rounds_by_year(user, competition):
    rounds = Round.visible_rounds(user).filter(series__competition=competition).order_by('-series__year', '-number')
    rounds_dict = dict()
    for round in rounds:
        if not round.series.year in rounds_dict:
            rounds_dict[round.series.year] = list()
        rounds_dict[round.series.year].append(round)
    return rounds_dict


def get_result_rounds(round):
    rounds = Round.objects.filter(visible=True, series=round.series, number__lte=round.number).order_by('number')
    return ','.join(str(r.id) for r in rounds)
