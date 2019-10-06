from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import ugettext_lazy as _

from trojsten.notifications import constants
from trojsten.notifications.models import Subscription
from trojsten.notifications.notification_types import RoundStarted, SubmitReviewed

notification_types = [RoundStarted, SubmitReviewed]


def _pretty_subscription_name(subscription):
    return "%s (%s)" % (subscription["name"], subscription["target"])


def _subscription_uid(type, target_pk):
    if not target_pk:
        return "%s" % (type,)
    return "%s:%s" % (type, target_pk)


class NotificationSettingsForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(NotificationSettingsForm, self).__init__(*args, **kwargs)
        self.user = user

        self.helper = FormHelper()
        self.helper.add_input(layout.Submit("notification_subscription_submit", _("Submit")))
        self.helper.form_show_labels = True

        subscribed_to = []
        for subscription in Subscription.objects.filter(
            user=self.user, status=constants.STATUS_SUBSCRIBED
        ):
            subscribed_to.append(
                _subscription_uid(subscription.notification_type, subscription.object_id)
            )

        allowed_subscriptions = []
        for notification_type in notification_types:
            targets = notification_type.get_available_targets(self.user)
            for target in targets:
                type = notification_type().get_identificator()
                allowed_subscriptions.append(
                    {
                        "name": notification_type.name,
                        "target": target,
                        "type": type,
                        "uid": _subscription_uid(type, target.pk if target else None),
                        "subscribed": _subscription_uid(type, target.pk if target else None)
                        in subscribed_to,
                    }
                )

        self.fields["subscriptions"] = forms.MultipleChoiceField(
            choices=[(s["uid"], _pretty_subscription_name(s)) for s in allowed_subscriptions],
            initial=[s["uid"] for s in allowed_subscriptions if s["subscribed"]],
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )
        self.fields["subscriptions"].label = _("Subscribed events")

    def save(self):
        enabled_subscriptions = self.cleaned_data["subscriptions"]

        subscribed_to = []
        for subscription in Subscription.objects.filter(
            user=self.user, status=constants.STATUS_SUBSCRIBED
        ):
            subscribed_to.append(
                _subscription_uid(subscription.notification_type, subscription.object_id)
            )

        for notification_type in notification_types:
            targets = notification_type.get_available_targets(self.user)
            for target in targets:
                type = notification_type().get_identificator()
                uid = _subscription_uid(type, target.pk)

                if uid in enabled_subscriptions and uid not in subscribed_to:
                    notification_type(target).subscribe(self.user)

                if uid not in enabled_subscriptions and uid in subscribed_to:
                    notification_type(target).unsubscribe(self.user)
