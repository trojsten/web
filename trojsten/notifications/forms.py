from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import ugettext_lazy as _

from trojsten.notifications.models import UnsubscribedChannel
from trojsten.notifications.settings import CHANNELS


class NotificationSettingsForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(NotificationSettingsForm, self).__init__(*args, **kwargs)
        self.user = user

        self.helper = FormHelper()
        self.helper.add_input(layout.Submit("notification_subscription_submit", _("Submit")))
        self.helper.form_show_labels = True

        unsubscribed_from = UnsubscribedChannel.objects.filter(user=user).values_list(
            "channel", flat=True
        )

        subscribed_to = []
        choices = []
        for channel in CHANNELS:
            choices.append((channel["key"], channel["name"]))

            if channel["key"] not in unsubscribed_from:
                subscribed_to.append(channel["key"])

        self.fields["subscribed"] = forms.MultipleChoiceField(
            choices=choices,
            initial=subscribed_to,
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )
        self.fields["subscribed"].label = _("Subscribed events")

    def save(self):
        new_subscribed = self.cleaned_data["subscribed"]

        unsubscribed_from = UnsubscribedChannel.objects.filter(user=self.user).values_list(
            "channel", flat=True
        )

        for channel in CHANNELS:
            if channel["key"] in unsubscribed_from and channel["key"] in new_subscribed:
                UnsubscribedChannel.objects.filter(user=self.user, channel=channel["key"]).delete()
            if channel["key"] not in unsubscribed_from and channel["key"] not in new_subscribed:
                UnsubscribedChannel.objects.get_or_create(user=self.user, channel=channel["key"])
