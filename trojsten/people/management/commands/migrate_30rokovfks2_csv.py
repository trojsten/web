from __future__ import unicode_literals

import csv
from collections import defaultdict
from datetime import datetime
import os


from django.core.management.base import NoArgsCommand
from django.db import connections, transaction
from django.db.models import Q
from django.utils.six.moves import input

from trojsten.people.helpers import get_similar_users
from trojsten.people.models import DuplicateUser, School, User, UserPropertyKey
from trojsten.people.management.commands.migrate_base_class import *


class Command(MigrateBaceCommand):
    help = 'Imports people and their related info from fks_csv.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('file', type=str)

    def handle_noargs(self, **options):
        super(Command, self).handle_noargs(**options)
        participants_file = options['file']

        participants = csv.DictReader(open(participants_file))
        idd = 0
        for l in participants:
            idd += 1
            if not l['Meno']:
                continue

            user = {
                'first_name': l['Meno'],
                'last_name': l['Priezvisko'],
                'email': l['E-mail'],
            }
            user_properties = [
                (MOBIL_PROPERTY, l['Telefon'].replace(" ", "").strip()),
                (BIRTH_NAME_PROPERTY, l['Rodne priezvisko']),
                (NICKNAME_PROPERTY, l['Prezyvka']),
                (COMPANY_PROPERTY, l['Posobisko']),
                (AFFILIATION_PROPERTY, l['Pozicia']),
                (MEMORY_PROPERTY, l['spomienka']),
                (LAST_CONTACT_PROPERTY, 2014),
            ]
            # TODO Adresa

            self.process_person(user, user_properties, CSV_ID_PROPERTY,
                                "30rokovFKS2_{0:d}".format(idd))

        self.print_stats()
