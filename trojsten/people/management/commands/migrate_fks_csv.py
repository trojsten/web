from __future__ import unicode_literals

import csv
import os

from trojsten.people.management.commands.migrate_base_class import MigrateBaseCommand

"""
Restore the mysql database dump and run (replace <passwd> and <user>)
Alternatively you can export these tables from phpAdmin.

for tn in adresa osoba riesitel skola
do
mysql -u<user> -p<passwd> fks -B -e "select * from \`$tn\`;"    \
| sed 's/\t/","/g;s/^/"/;s/$/"/;s/\n//g' > $tn.csv
done

mysql -u<user> -p<passwd> fks -B -e "   \
select riesitel_id, termin \
from seria as s, priklad as p, riesitel_priklady as rp, riesitel as r    \
where s.id = p.seria_id and rp.priklad_id = p.id and rp.riesitel_id = r.id;" \
| sed 's/\t/","/g;s/^/"/;s/$/"/;s/\n//g' > aktivita.csv
"""
# TODO vvysledkovky


class Command(MigrateBaseCommand):
    help = "Imports people and their related info from fks_csv."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("csv_directory", type=str, help="Directory containing all csv files.")

    def handle(self, **options):
        super(Command, self).handle(**options)
        base = options["csv_directory"]

        addresses_file = os.path.join(base, "adresa.csv")
        addresses = csv.DictReader(open(addresses_file))
        address_by_id = {}
        for address in addresses:
            address_by_id[address["id"]] = address

        schools_file = os.path.join(base, "skola.csv")
        schools = csv.DictReader(open(schools_file))
        for school in schools:
            abbr = school["skratka"].split(" ", 1)[0]
            addr = address_by_id[school["adresa_id"]]

            street = addr["ulica"]

            addr_name = school["nazov"] + ", " + street
            self.process_school(
                school["id"], abbr, school["nazov"], addr_name, street, addr["mesto"], addr["psc"]
            )

        activity_file = os.path.join(base, "aktivita.csv")
        activity = csv.DictReader(open(activity_file))
        for act in activity:
            idd = act["riesitel_id"]
            date = self.parse_dash_date(act["termin"])
            self.last_contact[idd].append(int(date.year))

        people_file = os.path.join(base, "osoba.csv")
        people = csv.DictReader(open(people_file))

        people_by_id = {}
        for person in people:
            people_by_id[person["id"]] = person

        participants_file = os.path.join(base, "riesitel.csv")
        participants = csv.DictReader(open(participants_file))

        for l in participants:
            idd = l["osoba_id"]
            person = people_by_id[idd]
            matura = l["rok_maturity"]
            self.last_contact[idd].append(int(matura) - 3)
            address = address_by_id[person["adresa_id"]]
            parsed_address = {
                "street": address["ulica"],
                "town": address["mesto"],
                "postal_code": address["psc"],
                "country": address["stat"],
            }
            user = {
                "first_name": person["meno"],
                "last_name": person["priezvisko"],
                "graduation": matura,
                "email": person["email"],
                "birth_date": self.parse_dash_date(person["datum_narodenia"]),
                "school_id": l["skola_id"],
            }

            user_properties = [(self.MOBIL_PROPERTY, person["telefon"].replace(" ", "").strip())]
            self.process_person(
                user, user_properties, self.FKS_ID_PROPERTY, idd, address=parsed_address
            )

        self.print_stats()
