from django.core.management.base import BaseCommand, CommandError

from trojsten.submit.helpers import update_submit
from trojsten.submit.models import Submit
from trojsten.contests.models import Task


class Command(BaseCommand):
    args = '<task_id task_id ...>'

    def handle(self, *args, **options):
        for task_id in args:
            try:
                task = Task.objects.get(pk=int(task_id))
            except Task.DoesNotExist:
                raise CommandError('Task "%s" does not exist' % task_id)

            for submit in Submit.objects.filter(task=task).all():
                update_submit(submit)

            self.stdout.write('Task "%s" successfully revalidated' % task_id)
