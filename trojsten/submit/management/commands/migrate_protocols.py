# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from trojsten.submit import constants
from trojsten.submit.models import Submit


def migrate_protocols(submit_type, *args, **kwargs):
    submits = Submit.objects.filter(protocol__isnull=True, submit_type=submit_type)
    logging.info("Unprocessed submit object count: {}".format(submits.count()))

    for submit in submits:
        try:
            protocol_path = submit.filepath.rsplit(".", 1)[0] + settings.PROTOCOL_FILE_EXTENSION
            with open(protocol_path) as protocol_file:
                submit.protocol = protocol_file.read()
                submit.save()
        except IOError as e:
            logging.warning(e)


class Command(BaseCommand):
    help = "Migrates protocols from filesystem to DB."

    def handle(self, *args, **kwargs):
        migrate_protocols(constants.SUBMIT_TYPE_SOURCE)
        migrate_protocols(constants.SUBMIT_TYPE_TESTABLE_ZIP)
