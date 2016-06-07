#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
try:
    from urllib import quote, unquote
except:
    from urllib.request import quote, unquote

from django.test import TestCase

from trojsten.reviews.forms import ZipForm
from trojsten.people.models import User


class ReviewZipFormTests(TestCase):
    def setUp(self):
        self.choices = [(47, 'Meno Priezvisko')]
        self.test_str = u'ľščťžýáíéúňďôä'
        self.test_str_win1250 = self.test_str.encode('cp1250')
        self.test_str_utf8 = self.test_str.encode('utf8')
        self.valid_files_win1250 = set([self.test_str_win1250])
        self.valid_files_utf8 = set([self.test_str_utf8])
        if sys.version_info[0] == 3:
            self.valid_files_win1250 = set([unquote(quote(self.test_str_win1250))])
            self.valid_files_utf8 = set([self.test_str_utf8.decode('utf8')])
        self.user = User(pk=47)
        self.user.save()
        pass

    def test_win_1250_valid(self):
        d = ZipForm({
            'filename': quote(self.test_str_win1250),
            'points': 3,
            'user': 47,
            'comment': self.test_str
        }, choices=self.choices, max_value=47, valid_files=self.valid_files_win1250)
        self.assertTrue(d.is_valid())

    def test_win_1250_encode(self):
        z = ZipForm(initial={
            'filename': self.test_str_win1250,
            'points': 3,
            'user': 47,
            'comment': self.test_str_win1250,
        }, choices=self.choices, max_value=47, valid_files=self.valid_files_win1250)

        self.assertEqual(z.initial['filename'], quote(self.test_str_win1250))
        self.assertEqual(z.initial['comment'], self.test_str)

    def test_utf8_valid(self):
        d = ZipForm({
            'filename': quote(self.test_str_utf8),
            'points': 3,
            'user': 47,
            'comment': self.test_str
        }, choices=self.choices, max_value=47, valid_files=self.valid_files_utf8)
        self.assertTrue(d.is_valid())

    def test_utf8_encode(self):
        z = ZipForm(initial={
            'filename': self.test_str_utf8,
            'points': 3,
            'user': 47,
            'comment': self.test_str_utf8,
        }, choices=self.choices, max_value=47, valid_files=self.valid_files_utf8)

        self.assertEqual(z.initial['filename'], quote(self.test_str_utf8))
        self.assertEqual(z.initial['comment'], self.test_str)
