from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import ugettext_lazy as _

from trojsten.notifications.constants import CHANNELS
from trojsten.notifications.models import UnsubscribedChannel


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

        self.fields["unsubscribed"] = forms.MultipleChoiceField(
            choices=CHANNELS.items(),
            initial=unsubscribed_from,
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )
        self.fields["unsubscribed"].label = _("Unsubscribed events")

    def save(self):
        new_unsubscribed = self.cleaned_data["unsubscribed"]

        unsubscribed_from = UnsubscribedChannel.objects.filter(user=self.user).values_list(
            "channel", flat=True
        )

        for channel in CHANNELS.keys():
            if channel in unsubscribed_from and channel not in new_unsubscribed:
                UnsubscribedChannel.objects.filter(user=self.user, channel=channel).delete()
            if channel not in unsubscribed_from and channel in new_unsubscribed:
                UnsubscribedChannel.objects.get_or_create(user=self.user, channel=channel)
