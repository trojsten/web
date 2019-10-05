import datetime

from django.test import TestCase

from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.people.models import User, UserProperty, UserPropertyKey

from .model_sanitizers import (
    GeneratorFieldSanitizer,
    TaskSanitizer,
    UserPropertySanitizer,
    UserSanitizer,
)


class GeneratorFieldSanitizerTest(TestCase):
    def test_data_replaced_by_generated_data(self):
        def fake_generator():
            return "generated_data"

        sanitized_data = GeneratorFieldSanitizer(fake_generator).sanitize("original_data")
        self.assertEquals(sanitized_data, "generated_data")


class TaskSanitizerTest(TestCase):
    def test_task_data_sanitized(self):
        c = Competition.objects.create(name="ABCD")
        s = Semester.objects.create(year=47, competition=c, number=1)
        r = Round.objects.create(number=3, semester=s, visible=True, solutions_visible=True)
        Task.objects.create(number=2, name="foo", round=r)

        TaskSanitizer().sanitize()

        sanitized_task = Task.objects.get()
        self.assertNotEquals(sanitized_task.name, "foo")


class UserSanitizerTest(TestCase):
    def test_user_data_sanitized(self):
        User.objects.create(
            username="foo",
            password="pwd",
            first_name="Ferko",
            last_name="Mrkvicka",
            birth_date=datetime.date(year=2000, month=1, day=1),
            email="ferko@example.com",
        )

        UserSanitizer().sanitize()

        sanitized_user = User.objects.get()
        self.assertNotEquals(sanitized_user.username, "foo")
        self.assertEquals(sanitized_user.password, "")
        self.assertNotEquals(sanitized_user.first_name, "Ferko")
        self.assertNotEquals(sanitized_user.last_name, "Mrkvicka")
        self.assertNotEquals(sanitized_user.birth_date, datetime.date(year=2000, month=1, day=1))
        self.assertNotEquals(sanitized_user.last_name, "ferko@example.com")


class UserPropertySanitizerTest(TestCase):
    def test_userproperty_data_sanitized(self):
        key = UserPropertyKey.objects.create(key_name="foo")
        user = User.objects.create(username="user")
        UserProperty.objects.create(user=user, key=key, value="bar")

        UserPropertySanitizer().sanitize()

        sanitized_userproperty = UserProperty.objects.get()
        self.assertEquals(sanitized_userproperty.key, key)
        self.assertNotEquals(sanitized_userproperty.value, "bar")
        self.assertEquals(len(sanitized_userproperty.value), 3)
