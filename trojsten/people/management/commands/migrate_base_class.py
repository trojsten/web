from __future__ import unicode_literals

from datetime import datetime
from imp import reload
from collections import defaultdict
import sys

from django.core.management.base import NoArgsCommand
from django.db import transaction
from django.db.models import Q
from django.utils.six.moves import input

from trojsten.people.helpers import get_similar_users
from trojsten.people.models import DuplicateUser, School, User, UserPropertyKey, UserProperty, Address

reload(sys)
sys.setdefaultencoding("utf-8")


class MigrateBaceCommand(NoArgsCommand):
    help = 'Base class for importing people.'

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
                            help='Create only a few users')

    def handle_noargs(self, **options):
        self.dry = options['dry']
        self.fast = options['fast']
        self.done_users = 0
        self.done_schools = 0
        if self.dry:
            self.stdout.write("Running dry run!")

        self.verbosity = options['verbosity']
        self.similar_users = []
        self.school_id_map = {}
        self.last_contact = defaultdict(list)

        CSV_ID_KEY = "csv ID"
        self.CSV_ID_PROPERTY = self.process_property(CSV_ID_KEY, "(.{1,20}_)?\d+")
        MOBIL_KEY = "Mobil"
        self.MOBIL_PROPERTY = self.process_property(MOBIL_KEY, "\+?\d+\/?\d+")
        NICKNAME_KEY = "Prezyvka"
        self.NICKNAME_PROPERTY = self.process_property(NICKNAME_KEY, ".{1,30}")
        BIRTH_NAME_KEY = "Rodne Meno"
        self.BIRTH_NAME_PROPERTY = self.process_property(BIRTH_NAME_KEY, ".{1,30}")
        LAST_CONTACT_KEY = "Posledny kontakt"
        # TODO  fix False and stupid values
        self.LAST_CONTACT_PROPERTY = self.process_property(LAST_CONTACT_KEY, "\d\d\d\d")
        FKS_ID_KEY = "FKS ID"
        self.FKS_ID_PROPERTY = self.process_property(FKS_ID_KEY, "\d+")
        KMS_ID_KEY = "KMS ID"
        self.KMS_ID_PROPERTY = self.process_property(KMS_ID_KEY, "\d+")
        KMS_CAMPS_KEY = "KMS sustredenia"
        self.KMS_CAMPS_PROPERTY = self.process_property(KMS_CAMPS_KEY, "\d+")
        KASPAR_ID_KEY = "KSP ID"
        self.KASPAR_ID_PROPERTY = self.process_property(KASPAR_ID_KEY, "\d+")
        KASPAR_NOTE_KEY = "KSP note"
        self.KASPAR_NOTE_PROPERTY = self.process_property(KASPAR_NOTE_KEY, ".*")
        KSP_CAMPS_KEY = "KSP sustredenia"
        self.KSP_CAMPS_PROPERTY = self.process_property(KSP_CAMPS_KEY, "\d+")
        MEMORY_KEY = "Spomienky"
        self.MEMORY_PROPERTY = self.process_property(MEMORY_KEY, ".*")
        COMPANY_KEY = "Posobisko"
        self.COMPANY_PROPERTY = self.process_property(COMPANY_KEY, ".*")
        AFFILIATION_KEY = "Pozicia"
        self.AFFILIATION_PROPERTY = self.process_property(AFFILIATION_KEY, ".*")

    @transaction.atomic
    def process_address(self, street, town, postal_code, country):
        return Address.objects.create(street=street, town=town, postal_code=postal_code, country=country)

    @transaction.atomic
    def process_school(self, old_id, abbr, name, addr_name, street,
                       city, zip_code):

        self.done_schools += 1
        if self.fast and self.done_schools > 100:
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
                self.stdout.write("Matched %r to %s" % (row,
                                                        candidates[0]))
            self.school_id_map[old_id] = candidates[0]
        elif len(candidates) > 1:
            self.stdout.write("Multiple candidates for %r:\n%s" % (
                row,
                "\n".join("%02d: %s" % (i, candidate)
                          for i, candidate in enumerate(candidates))
            ))
            try:
                choice = int(input("Choice (empty or invalid to create new): "))
                self.school_id_map[old_id] = candidates[choice]
            except (ValueError, KeyError):
                self.school_id_map[old_id] = self.create_school(*row)
        else:
            self.school_id_map[old_id] = self.create_school(*row)

    def create_school(self, abbr, name, addr_name, street,
                      city, zip_code):
        abbr += '?'  # Question mark denotes schools needing review.
        school = None
        if len(zip_code) > 10:
            # Swiss zip codes
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
            self.stdout.write("Created new school %s" % school)
        return school

    @transaction.atomic
    def process_person(self, user_args, user_properties, old_user_id_field, old_user_id, address=None):
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
        # If the user already exists in our database, skip.
        self.done_users += 1
        if self.fast and self.done_users > 100:
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
                self.stdout.write("Skipping user %s %s" % (first_name,
                                                           last_name))
            return None

        # The username needs to be unique, thus the ID.
        user_args['is_active'] = False

        if 'school_id' in user_args:
            school_id = user_args['school_id']
            del user_args['school_id']
            user_args['school'] = self.school_id_map.get(school_id)

        if self.verbosity >= 2:
            self.stdout.write("Creating user %s %s" % (first_name, last_name))

        new_user = None
        if self.dry:
            new_user = User(**user_args)
        else:
            addr = None
            if address:
                addr = self.process_address(address['street'],
                                            address['town'],
                                            address['postal_code'],
                                            address['country'])
                user_args['home_address'] = addr

            new_user = User.objects.create(**user_args)

            new_user.properties.create(key=old_user_id_field, value=old_user_id)

            # TODO last_contacted
            if old_user_id in self.last_contact:
                contacts = self.last_contact[old_user_id]
                valid_contacts = filter(lambda c: 1900 < c and c < 2017, contacts)
                if valid_contacts:
                    user_properties.append([self.LAST_CONTACT_PROPERTY, max(valid_contacts)])

            user_properties = list(filter(lambda x: x, user_properties))
            for key, value in user_properties:
                new_user.properties.create(key=key, value=value)

        similar_users = get_similar_users(new_user)
        if len(similar_users):
            names_of_similar = [(x.first_name, x.last_name) for x in similar_users]
            self.similar_users.append(((first_name, last_name), names_of_similar))
            if self.verbosity >= 2:
                self.stdout.write('Similar users: %s' % str(names_of_similar))
            if self.dry:
                pass
            else:
                DuplicateUser.objects.create(user=new_user)

        return new_user

    def print_stats(self):
        for conflict in self.similar_users:
            self.stdout.write("Conflicts: %s" % str(conflict))

        self.stdout.write("Conflict users: %d" % len(self.similar_users))

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
