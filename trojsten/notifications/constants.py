from django.utils.translation import ugettext_lazy as _

NOTIFICATION_SUBMIT_REVIEWED = "submit_reviewed"
NOTIFICATION_CONTEST_NEW_ROUND = "contest_new_round"

NOTIFICATION_PRETTY_NAMES = {
    NOTIFICATION_CONTEST_NEW_ROUND: _("New round"),
    NOTIFICATION_SUBMIT_REVIEWED: _("Submit reviewed"),
}
