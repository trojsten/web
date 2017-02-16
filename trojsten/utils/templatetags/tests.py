# -*- coding: utf-8 -*-

from django.test import TestCase

from .utils import choice_text


class ChoiceTextTests(TestCase):
    def test_full_list(self):
        choices = [
            (1, 'Hello'),
            (2, 'World'),
            (4, 'Foo'),
            (7, 'Bar'),
        ]

        self.assertEqual('Hello', choice_text(choices, 1))
        self.assertEqual('World', choice_text(choices, 2))
        self.assertEqual('Foo', choice_text(choices, 4))
        self.assertEqual('Bar', choice_text(choices, 7))
        self.assertEqual(None, choice_text(choices, 3))

    def test_empty(self):
        self.assertEqual(None, choice_text([], 3))
