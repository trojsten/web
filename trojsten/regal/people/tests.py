import random

from django.test import TestCase

from .helpers import get_similar_users
from .models import User


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
            similar_users, [user2.pk, user3.pk], transform=lambda u: u.pk, ordered=False
        )
        similar_users = get_similar_users(user2)
        self.assertQuerysetEqual(
            similar_users, [user.pk, user3.pk], transform=lambda u: u.pk, ordered=False
        )
        similar_users = get_similar_users(user3)
        self.assertQuerysetEqual(
            similar_users, [user.pk, user2.pk], transform=lambda u: u.pk, ordered=False
        )
        similar_users = get_similar_users(user1)
        self.assertQuerysetEqual(similar_users, [])
