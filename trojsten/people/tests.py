# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import random

from django.contrib.auth.models import Group
from django.http.request import HttpRequest
from django.test import TestCase

from trojsten.contests.models import Competition, Round, Series
from trojsten.contests.models import Task
from trojsten.schools.models import School
from .forms import TrojstenUserCreationForm, TrojstenUserChangeForm
from .helpers import get_similar_users, merge_users
from .models import Address, DuplicateUser, User, UserProperty, UserPropertyKey
from . import constants


def _create_random_user(**kwargs):
    def randomstring(length=16):
        alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'
        return ''.join(random.choice(alphabet) for _ in range(length))

    username = kwargs.pop('username', randomstring(30))
    return User.objects.create(username=username, **kwargs)


class GetSimilarUsersTests(TestCase):
    def test_get_similar_users(self):
        user = _create_random_user(first_name='Jozef', last_name='Novak')
        similar_users = get_similar_users(user)
        self.assertQuerysetEqual(similar_users, [])
        _create_random_user(first_name='Jozef', last_name='Mrkvicka')
        user1 = _create_random_user(first_name='Fero', last_name='Novak')
        similar_users = get_similar_users(user)
        self.assertQuerysetEqual(similar_users, [])
        user2 = _create_random_user(first_name='Jozef', last_name='Novak')
        user3 = _create_random_user(first_name='Jozef', last_name='Novak')
        similar_users = get_similar_users(user)
        self.assertQuerysetEqual(
            similar_users, [user2.pk, user3.pk], transform=lambda obj: obj.pk, ordered=False
        )
        similar_users = get_similar_users(user2)
        self.assertQuerysetEqual(
            similar_users, [user.pk, user3.pk], transform=lambda obj: obj.pk, ordered=False
        )
        similar_users = get_similar_users(user3)
        self.assertQuerysetEqual(
            similar_users, [user.pk, user2.pk], transform=lambda obj: obj.pk, ordered=False
        )
        similar_users = get_similar_users(user1)
        self.assertQuerysetEqual(similar_users, [])


class MergeUsersTests(TestCase):
    def setUp(self):
        self.tricko = UserPropertyKey.objects.create(key_name='Veľkosť trička')
        self.topanka = UserPropertyKey.objects.create(key_name='Veľkosť topánky')
        self.mobil = UserPropertyKey.objects.create(key_name='Mobil')
        self.telefon = UserPropertyKey.objects.create(key_name='Telefon')
        self.op = UserPropertyKey.objects.create(key_name='OP')
        self.address = Address.objects.create(
            street='Jablková 47', town='Dolný Kubín', postal_code='94742', country='Slovensko'
        )
        rnd = Round.objects.create(
            series=Series.objects.create(
                competition=Competition.objects.create(
                    name='Test competition'
                ),
                name='test',
                number=74,
                year=2024,
            ),
            number=2,
            visible=False,
            solutions_visible=False,
        )
        self.target_user = _create_random_user(
            first_name='Jozef', last_name='Novak', email='jozef@novak.sk', gender='M',
            graduation=2017,
        )
        self.source_user = _create_random_user(
            first_name='Jozef', last_name='Novak', email='jozef.novak@gmail.com', gender='M',
            graduation=2015, home_address=self.address,
        )
        UserProperty.objects.create(user=self.target_user, key=self.tricko, value='L')
        UserProperty.objects.create(user=self.target_user, key=self.topanka, value='47')
        UserProperty.objects.create(user=self.target_user, key=self.mobil, value='+421908123456')
        UserProperty.objects.create(user=self.source_user, key=self.tricko, value='M')
        UserProperty.objects.create(user=self.source_user, key=self.topanka, value='42')
        UserProperty.objects.create(user=self.source_user, key=self.telefon, value='+421212345678')
        UserProperty.objects.create(user=self.source_user, key=self.op, value='EA000444')
        Task.objects.create(
            name='Test task', reviewer=self.source_user, round=rnd, number=3, description_points=0,
            source_points=0, has_source=False, has_description=False,
        )

    def test_merge_fields_and_user_props(self):
        merge_users(
            self.target_user,
            self.source_user,
            ['graduation', 'home_address'],
            [self.tricko.pk, self.telefon.pk],
        )
        self.assertEqual(self.target_user.last_name, 'Novak')
        self.assertEqual(self.target_user.email, 'jozef@novak.sk')
        self.assertEqual(self.target_user.graduation, 2015)
        self.assertEqual(self.target_user.home_address, self.address)
        self.assertEqual(self.target_user.properties.get(key=self.topanka).value, '47')
        self.assertEqual(self.target_user.properties.get(key=self.mobil).value, '+421908123456')
        self.assertEqual(self.target_user.properties.get(key=self.tricko).value, 'M')
        with self.assertRaisesMessage(
            UserProperty.DoesNotExist, 'UserProperty matching query does not exist.'
        ):
            self.target_user.properties.get(key=self.op)
        with self.assertRaisesMessage(
            User.DoesNotExist, 'User matching query does not exist.'
        ):
            User.objects.get(pk=self.source_user.pk)

    def test_merge_fields_user_props_and_deleting_props(self):
        merge_users(
            self.target_user,
            self.source_user,
            ['email'],
            [self.topanka.pk, self.op.pk, self.mobil.pk],
        )
        self.assertEqual(self.target_user.last_name, 'Novak')
        self.assertEqual(self.target_user.email, 'jozef.novak@gmail.com')
        self.assertEqual(self.target_user.graduation, 2017)
        self.assertEqual(self.target_user.properties.get(key=self.topanka).value, '42')
        self.assertEqual(self.target_user.properties.get(key=self.tricko).value, 'L')
        with self.assertRaisesMessage(
            UserProperty.DoesNotExist, 'UserProperty matching query does not exist.'
        ):
            self.target_user.properties.get(key=self.mobil)
        with self.assertRaisesMessage(
            UserProperty.DoesNotExist, 'UserProperty matching query does not exist.'
        ):
            self.target_user.properties.get(key=self.telefon)
        with self.assertRaisesMessage(
            User.DoesNotExist, 'User matching query does not exist.'
        ):
            User.objects.get(pk=self.source_user.pk)

    def test_merge_related_fields(self):
        g1 = Group.objects.create(name='grp1')
        g2 = Group.objects.create(name='grp2')
        g3 = Group.objects.create(name='grp3')
        self.target_user.groups.add(g1)
        self.target_user.groups.add(g2)
        self.source_user.groups.add(g2)
        self.source_user.groups.add(g3)
        du = DuplicateUser.objects.create(user=self.source_user)
        merge_users(self.target_user, self.source_user, [], [])
        self.assertEqual(self.target_user.duplicateuser.pk, du.pk)
        self.assertQuerysetEqual(
            self.target_user.groups.all(), [g1.pk, g2.pk, g3.pk], transform=lambda obj: obj.pk,
            ordered=False,
        )
        with self.assertRaisesMessage(
            User.DoesNotExist, 'User matching query does not exist.'
        ):
            User.objects.get(pk=self.source_user.pk)


class UserFormTests(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.session = {}
        address = Address.objects.create(
            street='Matematicka 47', town='Algebrovo', postal_code='420 47',
            country='Slovensko'
        )
        School.objects.create(
            verbose_name='Iná škola', pk=1
        )
        self.school = School.objects.create(
            abbreviation='GJH', verbose_name='Gymnázium Janka Hraška', pk=2,
            street='Hronca 42', city='Bratislava', zip_code='123 45'
        )
        self.user = User.objects.create(
            username='janko4247', first_name='Janko', last_name='Hrasko', password='pass',
            gender='M', birth_date=datetime.date(1999, 9, 19), email='hrasko@example.com',
            mail_to_school=True, school=self.school, graduation=2018,
            home_address=address
        )
        self.form_data = {
            'username': 'mrkva',
            'password1': 'heslo',
            'password2': 'heslo',
            'first_name': 'Jožko',
            'last_name': 'Mrkvička',
            'gender': 'M',
            'mailing_option': constants.MAILING_OPTION_SCHOOL,
            'school': 2,
            'graduation': 2017,
            'street': 'Pekná 47',
            'town': 'Bratislava',
            'postal_code': '420 47',
            'country': 'Slovensko',
            'birth_date': datetime.date(2016, 8, 19),
            'email': 'mail@example.com'
        }
        self.form_data_corr = self.form_data.copy()
        self.form_data_corr.update({
            'username': 'mrkva2',
            'corr_street': 'Pekna 47',
            'corr_town': 'Krasno',
            'corr_postal_code': '842 47',
            'corr_country': 'Slovensko'
        })
        self.full_name = 'Jožko Mrkvička'

    def test_mailing_option_home(self):
        for data in [self.form_data, self.form_data_corr]:
            data['mailing_option'] = constants.MAILING_OPTION_HOME
            form = TrojstenUserCreationForm(data=data, request=self.request)
            self.assertTrue(form.is_valid())
            user = form.save()
            self.assertIsNone(user.mailing_address)
            address = user.get_mailing_address()
            self.assertEqual(
                [address.street, address.town, address.postal_code],
                [data['street'], data['town'], data['postal_code']]
            )

    def test_mailing_option_school(self):
        for data in [self.form_data, self.form_data_corr]:
            data['mailing_option'] = constants.MAILING_OPTION_SCHOOL
            form = TrojstenUserCreationForm(data=data, request=self.request)
            self.assertTrue(form.is_valid())
            user = form.save()
            self.assertTrue(user.mail_to_school)
            address = user.get_mailing_address()
            self.assertEqual(
                [address.recipient, address.street, address.town, address.postal_code],
                [self.full_name, self.school.street, self.school.city, self.school.zip_code]
            )

    def test_mailing_option_other(self):
        data = self.form_data
        data['mailing_option'] = constants.MAILING_OPTION_OTHER
        form = TrojstenUserCreationForm(data=data, request=self.request)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'corr_street': ['Toto pole je povinné.'],
            'corr_town': ['Toto pole je povinné.'],
            'corr_postal_code': ['Toto pole je povinné.'],
            'corr_country': ['Toto pole je povinné.']
        })
        data = self.form_data_corr
        data['mailing_option'] = constants.MAILING_OPTION_OTHER

        form = TrojstenUserCreationForm(data=data, request=self.request)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertFalse(user.mail_to_school)
        self.assertEqual([user.mailing_address.street, user.mailing_address.town,
                          user.mailing_address.postal_code, user.mailing_address.country],
                         [data['corr_street'], data['corr_town'],
                          data['corr_postal_code'], data['corr_country']])

    def test_user_creation_invalid_school(self):
        data = self.form_data
        data['school'] = 1
        data['mailing_option'] = constants.MAILING_OPTION_SCHOOL
        form = TrojstenUserCreationForm(data=data, request=self.request)
        self.assertFalse(form.is_valid())
        self.assertIn('mailing_option', form.errors)

    def test_user_creation_invalid_password(self):
        data = self.form_data
        data['password2'] = 'ine heslo'
        form = TrojstenUserCreationForm(data=data, request=self.request)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'password2': ['Heslo a jeho potvrdenie sa nezhodujú.']})

    def test_valid_initial_data(self):
        form = TrojstenUserChangeForm({}, user=self.user)
        form.data = form.initial
        self.assertTrue(form.is_valid())

    def test_valid_user_change(self):
        form = TrojstenUserChangeForm({}, user=self.user)
        form.data = form.initial
        form.data['mailing_option'] = constants.MAILING_OPTION_HOME
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertFalse(user.mail_to_school)

    def test_invalid_user_change(self):
        form = TrojstenUserChangeForm({}, user=self.user)
        form.data = form.initial
        form.data['mailing_option'] = constants.MAILING_OPTION_OTHER
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'corr_street': ['Toto pole je povinné.'],
            'corr_town': ['Toto pole je povinné.'],
            'corr_postal_code': ['Toto pole je povinné.'],
            'corr_country': ['Toto pole je povinné.']
        })

    def test_mailing_address_change(self):
        form = TrojstenUserChangeForm({}, user=self.user)
        form.data = form.initial
        street = 'Kukucinova 47'
        town = 'Sladkovicovo'
        postal_code = '420 47'
        country = 'Slovensko'

        form.data['mailing_option'] = constants.MAILING_OPTION_OTHER
        form.data['corr_street'] = street
        form.data['corr_town'] = town
        form.data['corr_postal_code'] = postal_code
        form.data['corr_country'] = country

        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertFalse(user.mail_to_school)
        self.assertEqual([user.mailing_address.street, user.mailing_address.town,
                          user.mailing_address.postal_code, user.mailing_address.country],
                         [street, town, postal_code, country])
