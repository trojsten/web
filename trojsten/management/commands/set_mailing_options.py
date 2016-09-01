from django.core.management.base import BaseCommand

from trojsten.people.models import User


class Command(BaseCommand):
    help = 'Set mailing_option for those users which don`t have mailing_option set.'

    def handle(self, *args, **options):
        count = 0
        for user in User.objects.all():
            if user.mailing_option == 'HOME' and user.mailing_address:
                option = 'OTHER'
                user.mailing_option = option
                self.stdout.write('In user {} set mailing_option to {}.'.format(
                    user.username, option))
                user.save()
                count += 1
        self.stdout.write('Changed %d users.' % count)
