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
    help = 'Imports people and their related info from kms_csv.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('file', type=str)

    def handle_noargs(self, **options):
        super(Command, self).handle_noargs(**options)
        base = options['file']
        participants_file = os.path.join(base, "riesitelia.csv")
        participants = csv.DictReader(open(participants_file))
        camps_file = os.path.join(base, "sustredenia.csv")
        camps = csv.DictReader(open(camps_file))
        camps_survived = defaultdict(int)
        last_contact = {}
        for camp in camps:
            idd = camp['id_riesitela'].strip()
            camps_survived[idd]+=1
            if camp['rok']:
                last_contact[idd] = max(last_contact.get(idd,0), int(camp['rok']))


        schools_file = os.path.join(base, "skoly.csv")
        schools = csv.DictReader(open(schools_file))
        for school in schools:
            abbr = school['skratka'].split(' ', 1)[0]
            addr_name = school['nazov'] + ", " + school['ulica']
            self.process_school(school['id'], abbr, school['nazov'], addr_name, school['ulica'],
                school['mesto'], school['PSC'])


        for l in participants:
            if not l['meno']:
                continue
            idd = l['id']
            last_contact[idd] = max(last_contact.get(idd,0), int(l['matura'])-3)
            user = {
                'first_name': l['meno'],
                'last_name': l['priezvisko'],
                'graduation': l['matura'],
                'email': l['email'],
                'birth_date': self.parse_dash_date(l['datnar']),
                'school_id': l['id_skoly']
            }

            #TODO parse addresses from string.
            'adresa_domov'
            'adresa_kores'

            user_properties = [
                (MOBIL_PROPERTY, l['mobil']),
                (KMS_CAMPS_PROPERTY, camps_survived[idd]),
                (LAST_CONTACT_PROPERTY, last_contact[idd])
            ]
            self.process_person(user, user_properties, KMS_ID_PROPERTY, int(idd))

        #TODO parse camps more precisely
        self.print_stats()

