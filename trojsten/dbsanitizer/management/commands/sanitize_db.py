from django.core.management.base import NoArgsCommand

from ...model_sanitizers import TaskSanitizer


class Command(NoArgsCommand):
    help = 'Sanitize datatabase, so any sensitive data is removed or anonymized.'

    def handle_noargs(self, **options):
        sanitizers = [TaskSanitizer()]
        for sanitizer in sanitizers:
            sanitizer.sanitize()
