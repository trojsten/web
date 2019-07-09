from __future__ import unicode_literals

import csv

from trojsten.people.management.commands.migrate_base_class import MigrateBaseCommand


class Command(MigrateBaseCommand):
    help = "Imports people and their related info from fks_csv."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("file", type=str)

    def handle(self, **options):
        super(Command, self).handle(**options)
        participants_file = options["file"]

        participants = csv.DictReader(open(participants_file))
        idd = 0
        for l in participants:
            idd += 1
            csv_id = "30rokovFKS2_{0:d}".format(idd)
            if not l["Meno"]:
                continue

            self.last_contact[csv_id].append(2014)
            user = {"first_name": l["Meno"], "last_name": l["Priezvisko"], "email": l["E-mail"]}
            user_properties = [
                (self.MOBIL_PROPERTY, l["Telefon"].replace(" ", "").strip()),
                (self.BIRTH_NAME_PROPERTY, l["Rodne priezvisko"]),
                (self.NICKNAME_PROPERTY, l["Prezyvka"]),
                (self.COMPANY_PROPERTY, l["Posobisko"]),
                (self.AFFILIATION_PROPERTY, l["Pozicia"]),
                (self.MEMORY_PROPERTY, l["spomienka"]),
            ]
            # TODO Adresa

            self.process_person(user, user_properties, self.CSV_ID_PROPERTY, csv_id)

        self.print_stats()
