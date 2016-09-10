# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

from django.contrib.auth.models import Group
from django.test import TestCase

from trojsten.contests.models import Competition, Round, Semester
from trojsten.contests.models import Task

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
