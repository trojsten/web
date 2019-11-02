from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from trojsten.notifications.models import Notification
from trojsten.people.models import User


class Command(BaseCommand):
    help = "Sends notification emails."

    def handle(self, *args, **options):
        base_query = Notification.objects.filter(was_email_sent=False, was_read=False)
        root_domain = Site.objects.get(pk=10).domain

        for user in base_query.values("user_id").distinct():
            user = User.objects.filter(pk=user["user_id"]).get()
            user_notifications = base_query.filter(user=user)

            mail_message = render_to_string(
                "trojsten/notifications/email.txt",
                {"user": user, "notifications": user_notifications, "domain": root_domain},
            )

            send_mail(
                _("You have new notifications from Trojsten"),
                mail_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )

            user_notifications.update(was_email_sent=True)
