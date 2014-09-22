from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand, CommandError
from django.utils.six.moves import input
from django.db import connections
from django.db.models import Q

from trojsten.regal.people.models import (User, UserProperty, Address,
    School)


class Command(NoArgsCommand):
    help = 'Imports people and their related info from kaspar.'

    def handle_noargs(self, **options):
        self.verbosity = options['verbosity']
        kaspar = connections['kaspar']
        c = kaspar.cursor()

        if self.verbosity >= 1:
            self.stdout.write("Migrating schools...")

        c.execute("""
            SELECT school_id, short, name, addr_name, addr_street,
                   addr_city, addr_zip
            FROM schools;
        """)
        school_id_map = dict()
        for row in c:
            kaspar_id, abbr, name, addr_name, street, city, zip_code = row
            candidates = School.objects.filter(
                Q(abbreviation__iexact=abbr) |
                Q(abbreviation__iexact=abbr + '?')
            )
            if len(candidates) == 1:
                if self.verbosity >= 2:
                    self.stdout.write("Matched %r to %s" % (row,
                                                            candidates[0]))
                school_id_map[kaspar_id] = candidates[0]
            elif len(candidates) > 1:
                self.stdout.write("Multiple candidates for %r:\n%s" % (
                    row,
                    "\n".join(("%02d: %s" % i, candidate)
                              for i, candidate in enumerate(candidates))
                ))
                try:
                    choice = int(input("Choice (empty to create new): "))
                except ValueError:
                    school_id_map[kaspar_id] = self.create_school(*row)
                else:
                    school_id_map[kaspar_id] = choices[choice]
            else:
                school_id_map[kaspar_id] = self.create_school(*row)

    def create_school(self, kaspar_id, abbr, name, addr_name, street,
                      city, zip_code):
        abbr += '?' # Question mark denotes schools needing review.
        school = School.objects.create(abbreviation=abbr,
                                       verbose_name=name,
                                       addr_name=addr_name,
                                       street=street,
                                       city=city,
                                       zip_code=zip_code)
        if self.verbosity >= 2:
            self.stdout.write("Created new school %s" % school)
        return school
