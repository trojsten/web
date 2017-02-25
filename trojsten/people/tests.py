# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import random

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http.request import HttpRequest
from django.test import TestCase
from django.utils import timezone

from trojsten.contests import constants as contests_constants
from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.rules.kms import KMS_COEFFICIENT_PROP_NAME
from trojsten.schools.models import School
from trojsten.submit.constants import SUBMIT_STATUS_IN_QUEUE, SUBMIT_TYPE_DESCRIPTION
from trojsten.submit.models import Submit

from . import constants
from .forms import TrojstenUserChangeForm, TrojstenUserCreationForm, SubmittedTasksFrom
from .helpers import get_similar_users, merge_users
from .models import Address, DuplicateUser, User, UserProperty, UserPropertyKey


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
            semester=Semester.objects.create(
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
        task = Task.objects.create(
            name='Test task', round=rnd, number=3, description_points=0,
            source_points=0, has_source=False, has_description=False,
        )
        task.assign_person(self.source_user, contests_constants.TASK_ROLE_REVIEWER)

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


class SettingsViewTests(TestCase):

    def setUp(self):
        self.url = reverse('trojsten_account_settings')
        self.element_login = UserPropertyKey.objects.create(
            key_name='Login na elementa', hidden=True)
        self.kaspar_id = UserPropertyKey.objects.create(key_name='kaspar_id', hidden=True)
        self.mobil = UserPropertyKey.objects.create(key_name='Mobil')
        self.tricko = UserPropertyKey.objects.create(key_name='Veľkosť trička')

    def test_login_redirect(self):
        response = self.client.get(self.url)
        redirect_to = '%s?next=%s' % (settings.LOGIN_URL, self.url)
        self.assertRedirects(response, redirect_to)

    def test_non_staff_see_only_visible_props(self):
        non_staff_user = User.objects.create_user(username='jozko', first_name='Jozko',
                                                  last_name='Mrkvicka')
        UserProperty.objects.create(user=non_staff_user, key=self.kaspar_id, value='1234')
        UserProperty.objects.create(user=non_staff_user, key=self.mobil, value='+421234567890')
        self.client.force_login(non_staff_user)
        response = self.client.get(self.url)
        self.assertContains(response, self.mobil.key_name)
        self.assertContains(response, '+421234567890')
        self.assertContains(response, self.tricko.key_name)
        self.assertNotContains(response, self.element_login)
        self.assertNotContains(response, self.kaspar_id)

    def test_staff_see_all_props(self):
        staff_user = User.objects.create_user(username='staff', first_name='Staff',
                                              last_name='Staff', is_staff=True)
        UserProperty.objects.create(user=staff_user, key=self.element_login, value='supercoollogin')
        UserProperty.objects.create(user=staff_user, key=self.mobil, value='+471234567890')
        self.client.force_login(staff_user)
        response = self.client.get(self.url)
        self.assertContains(response, self.mobil.key_name)
        self.assertContains(response, '+471234567890')
        self.assertContains(response, self.tricko.key_name)
        self.assertContains(response, self.element_login)
        self.assertContains(response, 'supercoollogin')
        self.assertContains(response, self.kaspar_id)


class EnvelopingTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name='staff')
        competition = Competition.objects.create(name='TestCompetition', pk=7, organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(number=1, name='Test semester', competition=competition,
                                           year=1)
        start = timezone.now() + timezone.timedelta(-8)
        end = timezone.now() + timezone.timedelta(-2)
        Round.objects.create(pk=1, number=1, semester=semester, visible=True,
                             solutions_visible=False, start_time=start,
                             end_time=end + timezone.timedelta(-1))
        self.round = Round.objects.create(pk=2, number=2, semester=semester, visible=True,
                                          solutions_visible=False, start_time=start, end_time=end)
        self.tasks = [None]
        for i in range(1, 11):
            task = Task.objects.create(number=i, name='Test task {}'.format(i), round=self.round)
            self.tasks.append(task)
        self.user = User.objects.create(username="TestUser", password="password",
                                        first_name="Jozko", last_name="Mrkvicka",
                                        graduation=timezone.now().year + 2)
        self.coeff_prop_key = UserPropertyKey.objects.create(key_name=KMS_COEFFICIENT_PROP_NAME)
        self.url = reverse('admin:submitted_tasks',
                           kwargs={'user_pk': self.user.pk, 'round_pk': self.round.pk})
        self.staff_user = User.objects.create_superuser('admin', 'mail@e.com', 'password')

    def test_correct_tasks_in_form(self):
        form = SubmittedTasksFrom(round=self.round)
        for i in range(1, 11):
            self.assertIn(str(i), form.fields.keys())

    def test_add_new_submits(self):
        data = {
            '2': 'on',
            '3': 'on',
            '5': 'on',
        }
        self.client.force_login(self.staff_user)
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        for task_number in data.keys():
            self.assertGreater(Submit.objects.filter(
                user=self.user, task__number=task_number, points=0,
                submit_type=SUBMIT_TYPE_DESCRIPTION,
                testing_status=SUBMIT_STATUS_IN_QUEUE).count(), 0)

    def test_round_change(self):
        self.client.force_login(self.staff_user)
        respose = self.client.post(self.url, {'round': '1'})
        self.assertEqual(respose.status_code, 200)
        self.assertEqual(respose.context['round'].pk, 1)
