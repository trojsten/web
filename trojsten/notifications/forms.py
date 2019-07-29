from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import ugettext_lazy as _
from django_nyt.models import Subscription

from trojsten.notifications import constants
from trojsten.notifications.models import IgnoredNotifications
from trojsten.notifications.utils import unsubscribe_from_subscription


def _pretty_subscription_name(subscription):
    pretty_name = constants.NOTIFICATION_PRETTY_NAMES[subscription.notification_type.key]
    if subscription.object_id:
        target = (
            subscription.notification_type.content_type.model_class()
            .objects.filter(pk=subscription.object_id)
            .get()
        )
        return "%s (%s)" % (pretty_name, target)
    else:
        return "%s" % (pretty_name,)


class NotificationSettingsForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(NotificationSettingsForm, self).__init__(*args, **kwargs)
        self.user = user

        self.helper = FormHelper()
        self.helper.add_input(layout.Submit("notification_subscription_submit", _("Submit")))
        self.helper.form_show_labels = True

        subscriptions = Subscription.objects.filter(settings__user=self.user)
        self.fields["subscriptions"] = forms.MultipleChoiceField(
            choices=[(s.pk, _pretty_subscription_name(s)) for s in subscriptions],
            initial=[s.pk for s in subscriptions],
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )
        self.fields["subscriptions"].label = _("Subscribed events")

        ignored = IgnoredNotifications.objects.filter(user=self.user)
        self.fields["ignored"] = forms.MultipleChoiceField(
            choices=[(s.pk, _pretty_subscription_name(s)) for s in ignored],
            initial=[s.pk for s in ignored],
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )
        self.fields["ignored"].label = _("Ignored events")

    def save(self):
        subscriptions = Subscription.objects.filter(settings__user=self.user)
        ignored = IgnoredNotifications.objects.filter(user=self.user)

        enabled_subscriptions = set(map(int, self.cleaned_data["subscriptions"]))
        enabled_ignored = set(map(int, self.cleaned_data["ignored"]))

        for subscription in ignored:
            if subscription.pk not in enabled_ignored:
                IgnoredNotifications.objects.filter(user=self.user, pk=subscription.pk).delete()

        for subscription in subscriptions:
            if subscription.pk not in enabled_subscriptions:
                unsubscribe_from_subscription(subscription)
