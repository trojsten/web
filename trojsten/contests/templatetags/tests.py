# -*- coding: utf-8 -*-
from datetime import timedelta

from django.template import Context, Template
from django.test import TestCase


class ProgressBarTest(TestCase):
    def setUp(self):
        self.template = Template(
            """
            {% load statements_parts %}
            {{ remaining|progress_time }}
            """
        )

    def assertTemplateContains(self, text, context):
        rendered_template = self.template.render(context)
        try:
            self.assertInHTML(text, rendered_template)
        except AssertionError:
            raise AssertionError(
                "Template does not contain {}.\n{}".format(text, rendered_template)
            )

    def test_progress_one_day(self):
        context = Context({"remaining": timedelta(days=1)})
        self.assertTemplateContains("1 deň", context)

    def test_progress_three_days(self):
        context = Context({"remaining": timedelta(days=3)})
        self.assertTemplateContains("3 dni", context)

    def test_progress_ten_days(self):
        context = Context({"remaining": timedelta(days=10)})
        self.assertTemplateContains("10 dní", context)

    def test_progress_one_hour(self):
        context = Context({"remaining": timedelta(hours=1)})
        self.assertTemplateContains("1 hodina", context)

    def test_progress_three_hours(self):
        context = Context({"remaining": timedelta(hours=3)})
        self.assertTemplateContains("3 hodiny", context)

    def test_progress_ten_hours(self):
        context = Context({"remaining": timedelta(hours=10)})
        self.assertTemplateContains("10 hodín", context)

    def test_progress_one_minute(self):
        context = Context({"remaining": timedelta(minutes=1)})
        self.assertTemplateContains("1 minúta", context)

    def test_progress_three_minutes(self):
        context = Context({"remaining": timedelta(minutes=3)})
        self.assertTemplateContains("3 minúty", context)

    def test_progress_ten_minutes(self):
        context = Context({"remaining": timedelta(minutes=10)})
        self.assertTemplateContains("10 minút", context)

    def test_progress_one_second(self):
        context = Context({"remaining": timedelta(seconds=1)})
        self.assertTemplateContains("1 sekunda", context)

    def test_progress_three_seconds(self):
        context = Context({"remaining": timedelta(seconds=3)})
        self.assertTemplateContains("3 sekundy", context)

    def test_progress_ten_seconds(self):
        context = Context({"remaining": timedelta(seconds=10)})
        self.assertTemplateContains("10 sekúnd", context)

    def test_progress_zero_seconds(self):
        context = Context({"remaining": timedelta(seconds=0)})
        self.assertTemplateContains("0 sekúnd", context)
