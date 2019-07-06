from django.core.management.base import BaseCommand

from ...model_sanitizers import ModelSanitizerManager


class Command(BaseCommand):
    help = "Sanitize datatabase, so any sensitive data is removed or anonymized."

    def handle(self, **options):
        ModelSanitizerManager.run()
