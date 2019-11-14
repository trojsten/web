from django.core.management.commands import makemessages


class Command(makemessages.Command):
    xgettext_options = makemessages.Command.xgettext_options + ["--add-location=never"]
