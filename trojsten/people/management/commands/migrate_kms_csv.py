from __future__ import unicode_literals

import csv
from collections import defaultdict
import os

from trojsten.people.management.commands.migrate_base_class import MigrateBaceCommand

"""
Restore the mysql database dump and run (replace <passwd> and <user>)
Alternatively you can export these tables from phpAdmin.

for tn in akcie riesitelia skoly sustredenia
do
mysql -u<user> -p<passwd> fks -B -e "select * from \`$tn\`;" \
| sed 's/\t/","/g;s/^/"/;s/$/"/;s/\n//g' > $tn.csv
done
"""


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
        for camp in camps:
            idd = camp['id_riesitela'].strip()
            camps_survived[idd] += 1
            if camp['rok']:
                self.last_contact[idd].append(int(camp['rok']))

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
            self.last_contact[idd].append(int(l['matura'])-3)
            user = {
                'first_name': l['meno'],
                'last_name': l['priezvisko'],
                'graduation': l['matura'],
                'email': l['email'],
                'birth_date': self.parse_dash_date(l['datnar']),
                'school_id': l['id_skoly']
            }

            # TODO parse addresses from string.
            'adresa_domov'
            'adresa_kores'

            user_properties = [
                (self.MOBIL_PROPERTY, l['mobil'].replace(" ", "").strip()),
                (self.KMS_CAMPS_PROPERTY, camps_survived[idd])
            ]
            self.process_person(user, user_properties, self.KMS_ID_PROPERTY, idd)

        # TODO parse camps more precisely
        self.print_stats()
