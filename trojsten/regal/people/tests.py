# -*- coding: utf-8 -*-
import random

from django.test import TestCase
from django.contrib.auth.models import Group

from .helpers import get_similar_users, merge_users
from .models import DuplicateUser, User, UserProperty, UserPropertyKey


class UserMergeTests(TestCase):
    def create_random_user(self, **kwargs):
        def randomstring(length=16):
            alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'
            return ''.join(random.choice(alphabet) for _ in range(length))

        username = kwargs.pop('username', randomstring(30))
        return User.objects.create(username=username, **kwargs)

    def test_get_similar_users(self):
        user = self.create_random_user(first_name='Jozef', last_name='Novak')
        similar_users = get_similar_users(user)
        self.assertQuerysetEqual(similar_users, [])
        self.create_random_user(first_name='Jozef', last_name='Mrkvicka')
        user1 = self.create_random_user(first_name='Fero', last_name='Novak')
        similar_users = get_similar_users(user)
        self.assertQuerysetEqual(similar_users, [])
        user2 = self.create_random_user(first_name='Jozef', last_name='Novak')
        user3 = self.create_random_user(first_name='Jozef', last_name='Novak')
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

    def test_merge_users(self):
        tricko = UserPropertyKey.objects.create(key_name=u'Veľkosť trička')
        topanka = UserPropertyKey.objects.create(key_name=u'Veľkosť topánky')
        mobil = UserPropertyKey.objects.create(key_name=u'Mobil')
        telefon = UserPropertyKey.objects.create(key_name=u'Telefon')
        op = UserPropertyKey.objects.create(key_name=u'OP')

        def create_users_to_merge():
            target_user = self.create_random_user(
                first_name='Jozef', last_name='Novak', email='jozef@novak.sk', gender='M',
                graduation=2017,
            )
            source_user = self.create_random_user(
                first_name='Jozef', last_name='Novak', email='jozef.novak@gmail.com', gender='M',
                graduation=2015,
            )
            UserProperty.objects.create(user=target_user, key=tricko, value='L')
            UserProperty.objects.create(user=target_user, key=topanka, value='47')
            UserProperty.objects.create(user=target_user, key=mobil, value='+421908123456')
            UserProperty.objects.create(user=source_user, key=tricko, value='M')
            UserProperty.objects.create(user=source_user, key=topanka, value='42')
            UserProperty.objects.create(user=source_user, key=telefon, value='+421212345678')
            UserProperty.objects.create(user=source_user, key=op, value='EA000444')
            return target_user, source_user

        # Test merging fields and user props
        target_user, source_user = create_users_to_merge()
        merge_users(target_user, source_user, ['graduation'], [tricko.pk, telefon.pk])
        self.assertEqual(target_user.last_name, 'Novak')
        self.assertEqual(target_user.email, 'jozef@novak.sk')
        self.assertEqual(target_user.graduation, 2015)
        self.assertEqual(target_user.properties.get(key=topanka).value, '47')
        self.assertEqual(target_user.properties.get(key=mobil).value, '+421908123456')
        self.assertEqual(target_user.properties.get(key=tricko).value, 'M')
        with self.assertRaisesMessage(
            UserProperty.DoesNotExist, 'UserProperty matching query does not exist.'
        ):
            target_user.properties.get(key=op)

        # Test merging fields, user props, and deleting user props
        target_user, source_user = create_users_to_merge()
        merge_users(target_user, source_user, ['email'], [topanka.pk, op.pk, mobil.pk])
        self.assertEqual(target_user.last_name, 'Novak')
        self.assertEqual(target_user.email, 'jozef.novak@gmail.com')
        self.assertEqual(target_user.graduation, 2017)
        self.assertEqual(target_user.properties.get(key=topanka).value, '42')
        self.assertEqual(target_user.properties.get(key=tricko).value, 'L')
        with self.assertRaisesMessage(
            UserProperty.DoesNotExist, 'UserProperty matching query does not exist.'
        ):
            target_user.properties.get(key=mobil)
        with self.assertRaisesMessage(
            UserProperty.DoesNotExist, 'UserProperty matching query does not exist.'
        ):
            target_user.properties.get(key=telefon)

        # Test merging related fields
        g1 = Group.objects.create(name='grp1')
        g2 = Group.objects.create(name='grp2')
        g3 = Group.objects.create(name='grp3')
        target_user, source_user = create_users_to_merge()
        target_user.groups.add(g1)
        target_user.groups.add(g2)
        source_user.groups.add(g2)
        source_user.groups.add(g3)
        du = DuplicateUser.objects.create(user=source_user)
        merge_users(target_user, source_user, [], [])
        self.assertEqual(target_user.duplicateuser.pk, du.pk)
        self.assertQuerysetEqual(
            target_user.groups.all(), [g1.pk, g2.pk, g3.pk], transform=lambda obj: obj.pk,
            ordered=False,
        )

        # Test the source user is deleted
