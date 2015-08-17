from django.conf import settings
from trojsten.utils.utils import import_string


_rules_instances = {}


def get_rules_for_competition(competition):
    pk = competition.pk
    if pk not in _rules_instances:
        _rules_instances[pk] = import_string(settings.COMPETITION_RULES.get(
            competition.pk,
            settings.DEFAULT_COMPETITION_RULES
        ))()
    return _rules_instances[pk]
