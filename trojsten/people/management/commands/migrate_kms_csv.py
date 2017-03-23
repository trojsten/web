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
from trojsten.people.management.commands.migrate_base_class import MigrateBaceCommand


class Command(MigrateBaceCommand):
    help = 'Imports people and their related info from kms_csv.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('file', type=str)

    def handle_noargs(self, **options):
        super(Command, self).handle_noargs(**options)
        base = options['file']
        riesitelia_file = os.path.join(base, "riesitelia.csv")
        riesitelia = csv.DictReader(open(riesitelia_file))
        sustredenia_file = os.path.join(base, "sustredenia.csv")
        sustredenia = csv.DictReader(open(sustredenia_file))
        ucasti = defaultdict(int)
        last_kontakt = {}
        for sustredko in sustredenia:
            idcko = sustredko['id_riesitela'].strip()
            ucasti[idcko]+=1
            if sustredko['rok']:
                last_kontakt[idcko] = max(last_kontakt.get(idcko,0), int(sustredko['rok']))


        skoly_file = os.path.join(base, "skoly.csv")
        skoly = csv.DictReader(open(skoly_file))
        for skola in skoly:
            abbr = skola['skratka'].split(' ', 1)[0]
            addr_name = skola['nazov'] + ", " + skola['ulica']
            self.process_school(skola['id'], abbr, skola['nazov'], addr_name, skola['ulica'],
                skola['mesto'], skola['PSC'])


        kms_id_key, _ = UserPropertyKey.objects.get_or_create(key_name="KMS ID")
        kms_sustredka, _ = UserPropertyKey.objects.get_or_create(key_name="KMS sustredenia")
        mobil, _ = UserPropertyKey.objects.get_or_create(key_name="Mobil")
        trojsten_contact, _ = UserPropertyKey.objects.get_or_create(key_name="Posledny kontakt")


        for l in riesitelia:
            if not l['meno']:
                continue
            idcko = l['id']
            last_kontakt[idcko] = max(last_kontakt.get(idcko,0), int(l['matura'])-3)
            user = {
                'first_name': l['meno'],
                'last_name': l['priezvisko'],
                'graduation': l['matura'],
                'email': l['email'],
                'birth_date': self.parse_date(l['datnar']),
                'school_id': l['id_skoly']
            }

            #TODO treba poparsovat adresy,
            'adresa_domov'
            'adresa_kores'

            user_properties = [
                (mobil, l['mobil']),
                (kms_sustredka, ucasti[idcko]),
                (trojsten_contact, last_kontakt[idcko])
            ]
            self.process_person(user, user_properties, kms_id_key, int(l['id']))

        #TODO akcie, sustredenia
        self.print_stats()



    def parse_date(self, date_string):
        # Remove any whitespace inside the string.
        date_string = date_string.replace(' ', '')
        if date_string == "0000-00-00":
            return None
        else:
            return datetime.strptime(date_string, '%Y-%m-%d')


