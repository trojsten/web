from __future__ import unicode_literals

from datetime import datetime
from imp import reload
from collections import defaultdict
import sys

from django.core.management import BaseCommand as NoArgsCommand
from django.db import transaction
from django.db.models import Q
from django.utils.six.moves import input

from trojsten.people.helpers import get_similar_users
from trojsten.people import constants
from trojsten.schools.models import School
from trojsten.people.models import DuplicateUser, User, UserPropertyKey, UserProperty, Address

reload(sys)
sys.setdefaultencoding("utf-8")


class MigrateBaseCommand(NoArgsCommand):
    help = 'Base class for importing people.'
    SCHOOLS_INF_FAST_RUN = 100
    USER_IN_FAST_RUN = 100

    def add_arguments(self, parser):
        parser.add_argument('--wet_run',
                            action='store_false',
                            dest='dry',
                            default=True,
                            help='Actually write something to DB')
        parser.add_argument('--fast',
                            action='store_true',
                            dest='fast',
                            default=False,
                            help='Create only the first {} users and {} schools'.format(
                                self.USER_IN_FAST_RUN, self.SCHOOLS_INF_FAST_RUN))

    def handle(self, **options):
        self.dry = options['dry']
        self.fast = options['fast']
        self.done_users = 0
        self.done_schools = 0
        if self.dry:
            self.stderr.write("Running dry run!")

        self.verbosity = options['verbosity']
        self.similar_users = []
        self.school_id_map = {}
        self.last_contact = defaultdict(list)

        self.CSV_ID_PROPERTY = self.process_property(
            constants.CSV_ID_PROPERTY_KEY, "(.{1,20}_)?\d+")
        self.MOBIL_PROPERTY = self.process_property(
            constants.MOBIL_PROPERTY_KEY, "\+?\d+\/?\d+")
        self.NICKNAME_PROPERTY = self.process_property(
            constants.NICKNAME_PROPERTY_KEY, ".{1,30}")
        self.BIRTH_NAME_PROPERTY = self.process_property(
            constants.BIRTH_NAME_PROPERTY_KEY, ".{1,30}")
        # TODO  fix False and stupid values
        self.LAST_CONTACT_PROPERTY = self.process_property(
            constants.LAST_CONTACT_PROPERTY_KEY, "\d\d\d\d")
        self.FKS_ID_PROPERTY = self.process_property(
            constants.FKS_ID_PROPERTY_KEY, "\d+")
        self.KMS_ID_PROPERTY = self.process_property(
            constants.KMS_ID_PROPERTY_KEY, "\d+")
        self.KMS_CAMPS_PROPERTY = self.process_property(
            constants.KMS_CAMPS_PROPERTY_KEY, "\d+")
        self.KASPAR_ID_PROPERTY = self.process_property(
            constants.KASPAR_ID_PROPERTY_KEY, "\d+")
        self.KASPAR_NOTE_PROPERTY = self.process_property(
            constants.KASPAR_NOTE_PROPERTY_KEY, ".*")
        self.KSP_CAMPS_PROPERTY = self.process_property(
            constants.KSP_CAMPS_PROPERTY_KEY, "\d+")
        self.MEMORY_PROPERTY = self.process_property(
            constants.MEMORY_PROPERTY_KEY, ".*")
        self.COMPANY_PROPERTY = self.process_property(
            constants.COMPANY_PROPERTY_KEY, ".*")
        self.AFFILIATION_PROPERTY = self.process_property(
            constants.AFFILIATION_PROPERTY_KEY, ".*")

    @transaction.atomic
    def process_school(self, old_id, abbr, name, addr_name, street,
                       city, zip_code):

        self.done_schools += 1
        if self.fast and self.done_schools > self.SCHOOLS_INF_FAST_RUN:
            return None
        # TODO improve this, do not work with abbreviations
        if not abbr:
            self.school_id_map[old_id] = None
            return

        candidates = School.objects.filter(
            Q(abbreviation__iexact=abbr) |
            Q(abbreviation__iexact=abbr + '?')
        )
        row = (abbr, name, addr_name, street, city, self.fix_string(zip_code))
        if len(candidates) == 1:
            if self.verbosity >= 2:
                self.stderr.write("Matched %r to %s" % (row,
                                                        candidates[0]))
            self.school_id_map[old_id] = candidates[0]
        elif len(candidates) > 1:
            self.stderr.write("Multiple candidates for %r:\n%s" % (
                row,
                "\n".join("%02d: %s" % (i, candidate)
                          for i, candidate in enumerate(candidates))
            ))
            try:
                choice = int(input("Choice (empty or invalid to create new): "))
                self.school_id_map[old_id] = candidates[choice]
            except (KeyError):
                self.school_id_map[old_id] = self.create_school(*row)
        else:
            self.school_id_map[old_id] = self.create_school(*row)

    def create_school(self, abbr, name, addr_name, street,
                      city, zip_code):
        abbr += '?'  # Question mark denotes schools needing review.
        school = None
        if len(zip_code) > 10:
            # Swiss zip codes are longer than 10 chars, but our db model does not allow
            # them so we skip them.
            zip_code = 0

        if self.dry:
            school = School(abbreviation=abbr,
                            verbose_name=name,
                            addr_name=addr_name,
                            street=street,
                            city=city,
                            zip_code=zip_code)
        else:
            school = School.objects.create(abbreviation=abbr,
                                           verbose_name=name,
                                           addr_name=addr_name,
                                           street=street,
                                           city=city,
                                           zip_code=zip_code)
        if self.verbosity >= 2:
            self.stderr.write("Created new school %s" % school)
        return school

    @transaction.atomic
    def process_person(self,
                       user_args,
                       user_properties,
                       old_user_id_field,
                       old_user_id,
                       address=None):
        """
        Args:
            user_args (dict): will be used for user constructor as is. Except for school_id.
            user_properties (list(tuple(UserPropertyKey, string))):
                will create additional user properties
            old_user_id_field (UserPropertyKey): old field that contained oser id
                (kaspar_id/ kms id ...), used for faster deduplication.
            old_user_id (int/string): old id
        user_args can have
        first_name, last_name, graduation, email, birth_date, school_id
        """
        # If we run in the fast mode and we already processed enough users, we skip this one.
        self.done_users += 1
        if self.fast and self.done_users > self.USER_IN_FAST_RUN:
            return None

        old_id_property = None
        if old_user_id:
            old_id_property = UserProperty.objects.filter(key=old_user_id_field, value=old_user_id)
        else:
            old_id_property = UserProperty.objects.none()

        first_name = user_args['first_name']
        last_name = user_args['last_name']
        if old_id_property.exists():
            if self.verbosity >= 2:
                self.stderr.write("Skipping user %s %s" % (first_name,
                                                           last_name))
            return None

        user_args['is_active'] = False

        if 'school_id' in user_args:
            school_id = user_args['school_id']
            del user_args['school_id']
            user_args['school'] = self.school_id_map.get(school_id)

        if self.verbosity >= 2:
            self.stderr.write("Creating user %s %s" % (first_name, last_name))

        new_user = None
        if self.dry:
            new_user = User(**user_args)
        else:
            if address:
                user_args['home_address'] = Address.objects.create(
                    street=address['street'], town=address['town'],
                    postal_code=address['postal_code'], country=address['country'])

            new_user = User.objects.create(**user_args)

            new_user.properties.create(key=old_user_id_field, value=old_user_id)

            # TODO last_contacted
            if old_user_id in self.last_contact:
                contacts = self.last_contact[old_user_id]
                valid_contacts = filter(lambda c: 1900 < c and c < 2017, contacts)
                if valid_contacts:
                    user_properties.append([self.LAST_CONTACT_PROPERTY, max(valid_contacts)])

            user_properties = [prop for prop in user_properties if prop is not None]
            for key, value in user_properties:
                new_user.properties.create(key=key, value=value)

        similar_users = get_similar_users(new_user)
        if len(similar_users):
            names_of_similar = [(user.first_name, user.last_name) for user in similar_users]
            self.similar_users.append(((first_name, last_name), names_of_similar))
            if self.verbosity >= 2:
                self.stderr.write('Similar users: %s' % str(names_of_similar))
            if not self.dry:
                DuplicateUser.objects.create(user=new_user)

        return new_user

    def print_stats(self):
        for conflict in self.similar_users:
            self.stderr.write("Conflicts: %s" % str(conflict))

        self.stderr.write("Conflict users: %d" % len(self.similar_users))

    def parse_dot_date(self, date_string):
        # Remove any whitespace inside the string.
        date_string = date_string.replace(' ', '')
        # Just hope that all dates are in the same format.
        return datetime.strptime(date_string, '%d.%m.%Y')

    def parse_dash_date(self, date_string):
        # Remove any whitespace inside the string.
        date_string = date_string.replace(' ', '')
        if date_string == "0000-00-00" or date_string == "NULL":
            return None
        else:
            return datetime.strptime(date_string, '%Y-%m-%d')

    def process_property(self, key_name, regexp=None):
        user_property = UserPropertyKey.objects.filter(key_name=key_name)
        if not user_property.exists():
            if self.dry:
                user_property = UserPropertyKey(key_name=key_name, regex=regexp)
            else:
                user_property = UserPropertyKey.objects.create(key_name=key_name, regex=regexp)
        else:
            user_property = user_property.first()
        return user_property

    def fix_string(self, string):
        return string.replace(" ", "").strip()
