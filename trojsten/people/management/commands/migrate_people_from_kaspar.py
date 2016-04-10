from __future__ import unicode_literals

from datetime import datetime

from django.core.management.base import NoArgsCommand, CommandError
from django.utils.six.moves import input
from django.db import connections, transaction
from django.db.models import Q

from trojsten.people.models import (User, UserPropertyKey, Address,
    School, DuplicateUser)

from trojsten.people.helpers import get_similar_users

# Kaspar property IDs
EMAIL_PROP = 1
BIRTHDAY_PROP = 2
# Labels for auto-generated properties
KASPAR_ID_LABEL = "kaspar ID"
KASPAR_NOTE_LABEL = "kaspar note"


class Command(NoArgsCommand):
    help = 'Imports people and their related info from kaspar.'

    def handle_noargs(self, **options):
        self.verbosity = options['verbosity']
        self.kaspar = connections['kaspar']
        c = self.kaspar.cursor()

        if self.verbosity >= 1:
            self.stdout.write("Migrating schools...")

        c.execute("""
            SELECT school_id, short, name, addr_name, addr_street,
                   addr_city, addr_zip
            FROM schools;
        """)
        self.school_id_map = dict()
        for row in c:
            self.process_school(*row)

        if self.verbosity >= 1:
            self.stdout.write("Creating/retrieving required UserPropertyKeys...")

        self.kaspar_id_key, _ = UserPropertyKey.objects.get_or_create(key_name=KASPAR_ID_LABEL)
        self.kaspar_note_key, _ = UserPropertyKey.objects.get_or_create(key_name=KASPAR_NOTE_LABEL)

        if self.verbosity >= 1:
            self.stdout.write("Migrating people...")

        c.execute("""
            SELECT man_id, firstname, lastname, school_id, finish, note
            FROM people;
        """)
        self.man_id_map = dict()
        # This loop takes O(N) queries and I don't care -- it's a one-time
        # background job anyway.
        for row in c:
            self.process_person(*row)

    @transaction.atomic
    def process_school(self, kaspar_id, abbr, name, addr_name, street,
                       city, zip_code):
        candidates = School.objects.filter(
            Q(abbreviation__iexact=abbr) |
            Q(abbreviation__iexact=abbr + '?')
        )
        row = (kaspar_id, abbr, name, addr_name, street, city, zip_code)
        if len(candidates) == 1:
            if self.verbosity >= 2:
                self.stdout.write("Matched %r to %s" % (row,
                                                        candidates[0]))
            self.school_id_map[kaspar_id] = candidates[0]
        elif len(candidates) > 1:
            self.stdout.write("Multiple candidates for %r:\n%s" % (
                row,
                "\n".join("%02d: %s" % (i, candidate)
                          for i, candidate in enumerate(candidates))
            ))
            try:
                choice = int(input("Choice (empty or invalid to create new): "))
                self.school_id_map[kaspar_id] = candidates[choice]
            except (ValueError, KeyError):
                self.school_id_map[kaspar_id] = self.create_school(*row)
        else:
            self.school_id_map[kaspar_id] = self.create_school(*row)

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

    @transaction.atomic
    def process_person(self, man_id, first_name, last_name, school_id,
                      grad_year, note):
        # If the user already exists in our database, skip.
        if self.kaspar_id_key.properties.filter(value=man_id).exists():
            if self.verbosity >= 2:
                self.stdout.write("Skipping user %s %s" % (first_name,
                                                           last_name))
                return

        new_user_args = {
            'first_name': first_name,
            'last_name': last_name,
            # The username needs to be unique, thus the ID.
            'username': '%s%s%d' % (first_name, last_name, man_id),
            'is_active': False,
            'school': self.school_id_map[school_id]
        }

        if grad_year:
            new_user_args['graduation'] = grad_year

        c = self.kaspar.cursor()
        c.execute("""
            SELECT ppt_id, value
            FROM people_prop
            WHERE people_prop.man_id = %s AND ppt_id IN (%s, %s);
        """, (man_id, EMAIL_PROP, BIRTHDAY_PROP))
        for prop_id, value in c:
            if prop_id == EMAIL_PROP:
                new_user_args['email'] = value
            elif prop_id == BIRTHDAY_PROP:
                try:
                    new_user_args['birth_date'] = self.parse_date(value)
                except ValueError:
                    # If we can't parse the date, give up.
                    pass
        c.close()

        if self.verbosity >= 2:
            self.stdout.write("Creating user %s %s" % (first_name, last_name))

        new_user = User.objects.create(**new_user_args)
        self.man_id_map[man_id] = new_user

        new_user.properties.create(key=self.kaspar_id_key, value=man_id)
        if note:
            new_user.properties.create(key=self.kaspar_note_key, value=note)
        similar_users = get_similar_users(new_user)
        if len(similar_users):
            if self.verbosity >= 2:
                self.stdout.write('Similar users: %s' % str(similar_users))
            DuplicateUser.objects.create(user=new_user)

    def parse_date(self, date_string):
        # Remove any whitespace inside the string.
        date_string = date_string.replace(' ', '')
        # Just hope that all dates are in the same format.
        return datetime.strptime(date_string, '%d.%m.%Y')
