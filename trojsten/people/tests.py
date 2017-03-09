# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import random
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http.request import HttpRequest
from django.test import TestCase
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from trojsten.contests import constants as contests_constants
from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.schools.models import School
from trojsten.submit.constants import (SUBMIT_PAPER_FILEPATH,
                                       SUBMIT_STATUS_IN_QUEUE,
                                       SUBMIT_STATUS_REVIEWED,
                                       SUBMIT_TYPE_DESCRIPTION)
from trojsten.submit.models import Submit
from trojsten.utils.test_utils import get_noexisting_id

from . import constants
from .constants import DEENVELOPING_NOT_REVIEWED_SYMBOL
from .forms import (AdditionalRegistrationForm, SubmittedTasksForm,
                    TrojstenUserChangeForm, TrojstenUserCreationForm)
from .helpers import (get_required_properties,
                      get_required_properties_by_competition,
                      get_similar_users, merge_users)
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


class UserTests(TestCase):
    def setUp(self):
        self.user = _create_random_user()
        self.element_login = UserPropertyKey.objects.create(
            key_name='Login na elementa', hidden=True)
        self.kaspar_id = UserPropertyKey.objects.create(key_name='kaspar_id', hidden=True)
        self.mobil = UserPropertyKey.objects.create(key_name='Mobil')
        self.tricko = UserPropertyKey.objects.create(key_name='Veľkosť trička')
        UserProperty.objects.create(user=self.user, key=self.element_login, value='supercoollogin')
        UserProperty.objects.create(user=self.user, key=self.mobil, value='+471234567890')
        UserProperty.objects.create(user=self.user, key=self.kaspar_id, value='1234')

    def test_valid_for_competition(self):
        competition = Competition.objects.create()
        competition.required_user_props.add(self.kaspar_id)
        competition.required_user_props.add(self.mobil)
        self.assertTrue(self.user.is_valid_for_competition(competition))

    def test_not_valid_for_competition(self):
        competition = Competition.objects.create()
        competition.required_user_props.add(self.element_login)
        competition.required_user_props.add(self.tricko)
        self.assertFalse(self.user.is_valid_for_competition(competition))


class PeopleApiTests(TestCase):
    def setUp(self):
        self.user = _create_random_user()
        self.competition = Competition.objects.create()
        self.url = reverse('people:switch_contest_participation')

    def test_ignore_competition(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {
            'competition': str(self.competition.pk),
            'value': 'true',
        })
        self.assertTrue(self.user.is_competition_ignored(self.competition))

    def test_unignore_competition(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {
            'competition': str(self.competition.pk),
            'value': 'false',
        })
        self.assertFalse(self.user.is_competition_ignored(self.competition))

    def test_ignore_competition_invalid_competition(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {
            'competition': str(get_noexisting_id(Competition)),
            'value': 'true',
        })
        self.assertFalse(self.user.is_competition_ignored(self.competition))

        self.client.post(self.url, {
            'value': 'true',
        })
        self.assertFalse(self.user.is_competition_ignored(self.competition))

        self.client.post(self.url, {
            'competition': "Hello",
            'value': 'true',
        })
        self.assertFalse(self.user.is_competition_ignored(self.competition))

    def test_ignore_competition_anonymous(self):
        response = self.client.post(self.url, {
            'competition': str(self.competition.pk),
            'value': 'true',
        })
        self.assertEqual(response.status_code, 401)


class DeenvelopingTests(TestCase):
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
            task = Task.objects.create(number=i, name='Test task {}'.format(i),
                                       round=self.round, description_points=9)
            self.tasks.append(task)
        self.new_user = User.objects.create(username="newuser", password="password",
                                            first_name="Jozko", last_name="Mrkvicka",
                                            graduation=timezone.now().year + 2)
        self.user_with_submits = User.objects.create(username="submituser", password="password",
                                                     first_name="Janko", last_name="Hrasko",
                                                     graduation=timezone.now().year + 2)
        self.url_new = reverse('admin:submitted_tasks',
                               kwargs={'user_pk': self.new_user.pk, 'round_pk': self.round.pk})
        self.url_submits = reverse('admin:submitted_tasks',
                                   kwargs={'user_pk': self.user_with_submits.pk,
                                           'round_pk': self.round.pk})
        self.staff_user = User.objects.create_superuser('admin', 'mail@e.com', 'password')

        for points in [0, 8, 9]:
            Submit.objects.create(
                task=self.tasks[7],
                user=self.user_with_submits,
                submit_type=SUBMIT_TYPE_DESCRIPTION,
                points=points,
                filepath='/riesenie.pdf',
                time=self.round.end_time,
            )
        Submit.objects.create(
            task=self.tasks[1],
            user=self.user_with_submits,
            submit_type=SUBMIT_TYPE_DESCRIPTION,
            points=0,
            filepath=SUBMIT_PAPER_FILEPATH,
            testing_status=SUBMIT_STATUS_IN_QUEUE,
            time=self.round.end_time,
        )

    def test_correct_tasks_in_form(self):
        form = SubmittedTasksForm(self.round)
        for i in range(1, 11):
            self.assertIn(str(i), form.fields.keys())

    def test_form_clean(self):
        form = SubmittedTasksForm(self.round, data={'1': 'xxx'})
        self.assertFalse(form.is_valid())
        form = SubmittedTasksForm(self.round, data={'1': '-42'})
        self.assertFalse(form.is_valid())
        form = SubmittedTasksForm(self.round, data={'1': '47'})
        self.assertFalse(form.is_valid())
        form = SubmittedTasksForm(self.round, data={'1': '7'})
        self.assertTrue(form.is_valid())

    def test_create_new_submits(self):
        data = {
            '2': DEENVELOPING_NOT_REVIEWED_SYMBOL,
            '3': DEENVELOPING_NOT_REVIEWED_SYMBOL,
            '5': DEENVELOPING_NOT_REVIEWED_SYMBOL,
        }
        self.client.force_login(self.staff_user)
        response = self.client.post(self.url_new, data, follow=True)
        self.assertEqual(response.status_code, 200)
        for task_number in data.keys():
            self.assertGreater(Submit.objects.filter(
                user=self.new_user, task__number=task_number, points=0,
                submit_type=SUBMIT_TYPE_DESCRIPTION,
                testing_status=SUBMIT_STATUS_IN_QUEUE).count(), 0)

    def test_add_subits_to_existing_submits(self):
        data = {
            '1': DEENVELOPING_NOT_REVIEWED_SYMBOL,
            '4': DEENVELOPING_NOT_REVIEWED_SYMBOL,
            '7': DEENVELOPING_NOT_REVIEWED_SYMBOL,
        }
        self.client.force_login(self.staff_user)
        response = self.client.post(self.url_submits, data, follow=True)
        self.assertEqual(response.status_code, 200)
        for task_number in data.keys():
            self.assertGreater(Submit.objects.filter(
                user=self.user_with_submits, task__number=task_number,
                submit_type=SUBMIT_TYPE_DESCRIPTION).count(), 0)

    def test_round_change(self):
        self.client.force_login(self.staff_user)
        respose = self.client.post(self.url_new, {'round': '1'})
        self.assertEqual(respose.status_code, 200)
        self.assertEqual(respose.context['round'].pk, 1)

    def test_delete_paprer_submit(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(self.url_submits,
                                    {'7': DEENVELOPING_NOT_REVIEWED_SYMBOL}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Submit.objects.filter(
            task=self.tasks[1], user=self.user_with_submits, submit_type=SUBMIT_TYPE_DESCRIPTION,
            filepath=SUBMIT_PAPER_FILEPATH,
        ).count(), 0)

    def test_not_delete_electronic_submit(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(self.url_submits,
                                    {'1': DEENVELOPING_NOT_REVIEWED_SYMBOL}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Submit.objects.filter(
            task=self.tasks[7], user=self.user_with_submits, submit_type=SUBMIT_TYPE_DESCRIPTION,
        ).count(), 3)

    def test_add_and_delete_submits(self):
        data = {
            '2': DEENVELOPING_NOT_REVIEWED_SYMBOL,
            '3': DEENVELOPING_NOT_REVIEWED_SYMBOL,
            '4': DEENVELOPING_NOT_REVIEWED_SYMBOL,
            '7': DEENVELOPING_NOT_REVIEWED_SYMBOL,
        }
        self.client.force_login(self.staff_user)
        response = self.client.post(self.url_submits, data, follow=True)
        self.assertEqual(response.status_code, 200)
        for task_number in data.keys():
            self.assertGreater(Submit.objects.filter(
                user=self.user_with_submits, task__number=task_number,
                submit_type=SUBMIT_TYPE_DESCRIPTION).count(), 0)
        self.assertEqual(Submit.objects.filter(
            user=self.user_with_submits, task__number=1,
            submit_type=SUBMIT_TYPE_DESCRIPTION).count(), 0)

    def test_submit_new_points(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(self.url_new, {'1': '7', '2': '4.47'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Submit.objects.filter(
            user=self.new_user, task=self.tasks[1], points=7,
            submit_type=SUBMIT_TYPE_DESCRIPTION, testing_status=SUBMIT_STATUS_REVIEWED
        ).count(), 1)
        self.assertEqual(Submit.objects.filter(
            user=self.new_user, task=self.tasks[2], points=Decimal('4.47'),
            submit_type=SUBMIT_TYPE_DESCRIPTION, testing_status=SUBMIT_STATUS_REVIEWED
        ).count(), 1)

    def test_add_submit_points(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(self.url_submits, {'7': '7'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Submit.objects.filter(
            user=self.user_with_submits, task=self.tasks[7], points=7,
            submit_type=SUBMIT_TYPE_DESCRIPTION, testing_status=SUBMIT_STATUS_REVIEWED
        ).count(), 1)

    def test_edit_submit_points(self):
        Submit.objects.create(
            user=self.user_with_submits, task=self.tasks[10],
            time=self.round.end_time + timezone.timedelta(seconds=-1),
            filepath=SUBMIT_PAPER_FILEPATH, testing_status=SUBMIT_STATUS_REVIEWED,
            submit_type=SUBMIT_TYPE_DESCRIPTION, points=4
        )
        self.client.force_login(self.staff_user)
        response = self.client.post(self.url_submits, {'10': '9'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Submit.objects.filter(
            user=self.user_with_submits, task=self.tasks[10], points=9,
            submit_type=SUBMIT_TYPE_DESCRIPTION, testing_status=SUBMIT_STATUS_REVIEWED
        ).count(), 1)


class AdditionalRegistrationFormTest(TestCase):
    def setUp(self):
        self.user = _create_random_user()
        self.key1 = UserPropertyKey.objects.create(key_name='key1', regex='[0-9]+')
        self.key2 = UserPropertyKey.objects.create(key_name='key2')
        self.key3 = UserPropertyKey.objects.create(key_name='key3')
        self.key4 = UserPropertyKey.objects.create(key_name='key4')
        self.key5 = UserPropertyKey.objects.create(key_name='key5')

    def test_field_name(self):
        self.assertEqual('user_prop_%s' % self.key1.pk, AdditionalRegistrationForm._field_name(self.key1))

    def test_form_fields(self):
        keys = [self.key1, self.key2, self.key3, self.key4]
        form = AdditionalRegistrationForm(self.user, keys)
        self.assertListEqual(list(map(lambda k: AdditionalRegistrationForm._field_name(k), keys)), form.fields.keys())

    def test_clean_bad_regex(self):
        keys = [self.key1]
        form = AdditionalRegistrationForm(
            self.user, keys, {
                AdditionalRegistrationForm._field_name(self.key1): 'hello'
            }
        )
        self.assertFalse(form.is_valid())

    def test_clean_missing_value(self):
        keys = [self.key2, self.key3]
        form = AdditionalRegistrationForm(
            self.user, keys, {
                AdditionalRegistrationForm._field_name(self.key2): 'hello'
            }
        )
        self.assertFalse(form.is_valid())

    def test_clean(self):
        keys = [self.key1, self.key2, self.key3]
        form = AdditionalRegistrationForm(
            self.user, keys, {
                AdditionalRegistrationForm._field_name(self.key1): '47',
                AdditionalRegistrationForm._field_name(self.key2): 'hello',
                AdditionalRegistrationForm._field_name(self.key3): 'world',
            }
        )
        self.assertTrue(form.is_valid())

    def test_save(self):
        keys = [self.key1, self.key2, self.key3]
        form = AdditionalRegistrationForm(
            self.user, keys, {
                AdditionalRegistrationForm._field_name(self.key1): '47',
                AdditionalRegistrationForm._field_name(self.key2): 'hello',
                AdditionalRegistrationForm._field_name(self.key3): 'world',
            }
        )
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual('47', self.user.properties.get(key=self.key1).value)
        self.assertEqual('hello', self.user.properties.get(key=self.key2).value)
        self.assertEqual('world', self.user.properties.get(key=self.key3).value)


class AdditionalRegistrationHelpersTest(TestCase):
    def setUp(self):
        self.user = _create_random_user()
        self.key1 = UserPropertyKey.objects.create(key_name='key1')
        self.key2 = UserPropertyKey.objects.create(key_name='key2')
        self.key3 = UserPropertyKey.objects.create(key_name='key3')
        self.key4 = UserPropertyKey.objects.create(key_name='key4')
        self.key5 = UserPropertyKey.objects.create(key_name='key5')
        self.key6 = UserPropertyKey.objects.create(key_name='key6')
        UserProperty.objects.create(user=self.user, key=self.key1, value='value1')
        UserProperty.objects.create(user=self.user, key=self.key2, value='value2')
        self.competition = Competition.objects.create()
        self.competition.sites.add(settings.SITE_ID)
        self.competition.required_user_props.add(self.key1)
        self.competition.required_user_props.add(self.key3)
        self.competition2 = Competition.objects.create()
        self.competition2.sites.add(settings.SITE_ID)
        self.competition2.required_user_props.add(self.key2)
        self.competition2.required_user_props.add(self.key4)
        self.competition2.required_user_props.add(self.key6)

    def test_required_properties_by_competition(self):
        self.assertDictEqual(
            {
                self.competition: {self.key3},
                self.competition2: {self.key4, self.key6}
            },
            get_required_properties_by_competition(self.user)
        )

    def test_required_properties(self):
        self.assertSetEqual(
            {self.key3, self.key4, self.key6},
            get_required_properties(self.user)
        )


# @TODO: View tests
class AdditionalRegistrationViewsTest(TestCase):
    def setUp(self):
        self.url = reverse('additional_registration')
        self.user = _create_random_user()

    def test_no_login(self):
        response = self.client.get(self.url)
        redirect_to = '%s?next=%s' % (settings.LOGIN_URL, self.url)
        self.assertRedirects(response, redirect_to)

    def test_all_set(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, _('You have already filled all required properties.'))

    def test_props_required(self):
        key1 = UserPropertyKey.objects.create(key_name='key1')
        key2 = UserPropertyKey.objects.create(key_name='key2')
        competition = Competition.objects.create()
        competition.sites.add(settings.SITE_ID)
        competition.required_user_props.add(key1)
        competition2 = Competition.objects.create()
        competition2.sites.add(settings.SITE_ID)
        competition2.required_user_props.add(key2)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertContains(response, key1.key_name)
        self.assertContains(response, key2.key_name)
