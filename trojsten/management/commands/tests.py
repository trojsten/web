from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from trojsten.people.models import User, Address


class SetMailingOptionsTest(TestCase):
    def setUp(self):
        home_address = Address.objects.create(street='Pekna 47')
        other_address = Address.objects.create(street='Mlynska dolina')
        self.home_user = User.objects.create(username='home', home_address=home_address)
        self.other_user = User.objects.create(username='other', home_address=home_address,
                                              mailing_address=other_address)
        self.school_user = User.objects.create(username='school', home_address=home_address,
                                               mailing_option='SCHOOL')
        self.home_set_user = User.objects.create(username='homey', home_address=home_address,
                                                 mailing_option='HOME')

    def test_set_mailing_option(self):
        call_command('set_mailing_options')
        other_user = User.objects.get(username='other')
        self.assertEqual(self.home_user.mailing_option, 'HOME')
        self.assertEqual(other_user.mailing_option, 'OTHER')
        self.assertEqual(self.school_user.mailing_option, 'SCHOOL')
        self.assertEqual(self.home_set_user.mailing_option, 'HOME')
