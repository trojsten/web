from django.core.management.base import NoArgsCommand

from ...model_santizers import TaskSantizer


class Command(NoArgsCommand):
    help = 'Santize datatabase, so any sensitive data is removed or anonymized.'

    def handle_noargs(self, **options):
        santizers = [TaskSantizer()]
        for santizer in santizers:
            santizer.santize()
