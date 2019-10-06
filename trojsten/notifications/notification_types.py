from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import trojsten.notifications.constants as notification_constants
from trojsten.contests.models import Competition
from trojsten.notifications.models import Notification, Subscription


class NotificationType:
    name = ""

    def __init__(self, target_model=None):
        self.target_model = target_model

        self.content_type = None
        self.object_id = None
        if target_model is not None:
            self.content_type = ContentType.objects.get_for_model(target_model)
            self.object_id = target_model.pk

    def get_identificator(self):
        """Returns identificator of this notification type."""
        return self.__class__.__name__

    def get_message(self, context={}):
        """
        Returns notification message to be used in user interface.

        You should override this in your notification type.
        """
        raise NotImplementedError()

    @staticmethod
    def get_available_targets(user_model=None):
        """
        Returns QuerySet (or other iterable) of available targets.
        Used in notification settings UI.

        You should override this in your notification type.
        """
        raise NotImplementedError()

    def get_absolute_url(self, context={}):
        """
        Get URL this notification will link to.

        You should override this in your notification type.
        """
        raise NotImplementedError()

    def subscribe_unless_unsubscibed(self, user_model):
        """
        Subscribes user to this notification type, if this user did not unsubscribe manually before.
        Returns True if new subscription was created,
        False if user is already subscribed / unsubscribed.
        """
        if not Subscription.objects.filter(
            notification_type=self.get_identificator(),
            subscription__user=user_model,
            content_type=self.content_type,
            object_id=self.object_id,
        ).exists():
            self.subscribe(user_model)
            return True
        return False

    def subscribe(self, user_model):
        """
        Subscribes user to this notification type.
        """
        obj, created = Subscription.objects.update_or_create(
            notification_type=self.get_identificator(),
            subscription__user=user_model,
            content_type=self.content_type,
            object_id=self.object_id,
            defaults={"status": notification_constants.STATUS_SUBSCRIBED},
        )

        return obj

    def unsubscribe(self, user_model):
        """
        Unsubscribes user from this notification type.
        """

        obj, created = Subscription.objects.update_or_create(
            notification_type=self.get_identificator(),
            subscription__user=user_model,
            content_type=self.content_type,
            object_id=self.object_id,
            defaults={"status": notification_constants.STATUS_UNSUBSCRIBED},
        )

        return obj

    def dispatch(self, context={}):
        """
        Creates notifications for every subscribed user.
        """
        subscriptions = Subscription.objects.filter(
            content_type=self.content_type,
            object_id=self.object_id,
            status=notification_constants.STATUS_SUBSCRIBED,
        )
        for subscription in subscriptions:
            Notification.objects.create(
                subscription=subscription,
                message=self.get_message(context),
                url=self.get_absolute_url(context),
            )


class RoundStarted(NotificationType):
    name = _("New round started")

    @staticmethod
    def get_available_targets(user_model=None):
        return Competition.objects.all()

    def get_message(self, context={}):
        return _("Round %(round)s has started!" % {"round": context["round"]})

    def get_absolute_url(self, context={}):
        site = Site.objects.get_current()
        return "//%(domain)s%(url)s" % {
            "domain": site.domain,
            "url": reverse("task_list", args=(context["round"].pk,)),
        }


class SubmitReviewed(NotificationType):
    name = _("Your submit was reviewed")

    @staticmethod
    def get_available_targets(user_model=None):
        return [user_model]

    def get_message(self, context={}):
        return _(
            'Your description for "%(task)s" has been reviewed. You earned %(points)d points!'
        ) % {"task": context["task"], "points": context["points"]}

    def get_absolute_url(self, context={}):
        site = Site.objects.get_current()
        return "//%(domain)s%(url)s" % {
            "domain": site.domain,
            "url": reverse("task_submit_page", args=(context["task"].pk,)),
        }
