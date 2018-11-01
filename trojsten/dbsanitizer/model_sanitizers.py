# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string

from bulk_update.helper import bulk_update
from faker import Factory

from trojsten.people.models import User, UserProperty
from trojsten.contests.models import Task

accent_chars_lowercase = 'äřéŕťýúíóôášďěüöůĺľžčň'
accent_chars_uppercase = accent_chars_lowercase.upper()
accent_chars = accent_chars_lowercase + accent_chars_uppercase

fake = Factory.create()


class BaseFieldSantizer(object):
    def sanitize(self, data):
        return data


class GeneratorFieldSanitizer(BaseFieldSantizer):
    def __init__(self, generator):
        self.generator = generator

    def sanitize(self, data):
        return self.generator()


class RandomStringGenerator(object):
    def __init__(self, alphabet, length=None, min_length=None, max_length=None,
                 mapping_function=None):
        if length is not None and (min_length is not None or max_length is not None):
            raise AttributeError('Cannot set min_length or max_length together with length')
        if length is None and (min_length is None or max_length is None):
            raise AttributeError(
                'You have to specify either the min_length and the max_length, or the length'
            )
        if length is not None:
            self.min_length = self.max_length = length
        else:
            self.min_length = min_length
            self.max_length = max_length
        self.alphabet = alphabet
        self.mapping_function = mapping_function

    def __call__(self):
        res = ''.join(
            random.choice(self.alphabet)
            for _ in range(random.randrange(self.min_length, self.max_length))
        )
        return self.mapping_function(res) if self.mapping_function else res


class EmptyStringGenerator():
    def __call__(self):
        return ''


class TitleGenerator(RandomStringGenerator):
    def __init__(self):
        alphabet = string.ascii_lowercase*3 + accent_chars_lowercase + '     '
        super(TitleGenerator, self).__init__(
            alphabet, min_length=5, max_length=20, mapping_function=lambda s: s.title()
        )


class UserNameGenerator(RandomStringGenerator):
    def __init__(self):
        super(UserNameGenerator, self).__init__(
            string.ascii_lowercase+string.digits, min_length=4, max_length=10
        )


class RandomDateGenerator(object):
    pass


class ModelSanitizerManager(object):
    _sanitizers = list()

    @classmethod
    def run(cls):
        for sanitizer in cls._sanitizers:
            sanitizer.sanitize()

    @classmethod
    def register(cls, sanitizer):
        cls._sanitizers.append(sanitizer)


class BaseModelSanitizer(object):
    model = None
    field_sanitizers = dict()

    def get_objects(self):
        return self.model.objects.all()

    def sanitize_single_object(self, obj, save=False):
        for field, field_sanitizer in self.field_sanitizers.items():
            setattr(obj, field, field_sanitizer.sanitize(getattr(obj, field)))
        if save:
            obj.save()
        return obj

    def sanitize(self):
        objects = self.get_objects()
        for obj in objects:
            self.sanitize_single_object(obj)
        bulk_update(objects, update_fields=self.field_sanitizers.keys())


class TaskSanitizer(BaseModelSanitizer):
    model = Task
    field_sanitizers = {
        'name': GeneratorFieldSanitizer(TitleGenerator()),
    }


class UserSanitizer(BaseModelSanitizer):
    model = User
    field_sanitizers = {
        'password': GeneratorFieldSanitizer(EmptyStringGenerator()),
        'username': GeneratorFieldSanitizer(UserNameGenerator()),
        'first_name': GeneratorFieldSanitizer(fake.first_name),
        'last_name': GeneratorFieldSanitizer(fake.last_name),
        'birth_date': GeneratorFieldSanitizer(
            lambda: fake.date_time_between(start_date="-20y", end_date="-10y")
        ),
        'email': GeneratorFieldSanitizer(fake.email),
    }


class SmartStringSanitizer(BaseFieldSantizer):
    def transform_char(self, c):
        keep_chars = string.punctuation + string.whitespace
        alphabet = ''
        if ('A' <= c <= 'Z') or (c in accent_chars_uppercase):
            alphabet = string.ascii_uppercase*3 + accent_chars_uppercase
        elif ('a' <= c <= 'z') or (c in accent_chars_lowercase):
            alphabet = string.ascii_lowercase*3 + accent_chars_lowercase
        elif '0' <= c <= '9':
            alphabet = string.digits
        elif c in keep_chars:
            return c
        else:
            return '<?>'
        return random.choice(alphabet)

    def sanitize(self, data):
        return ''.join(map(self.transform_char, data))


class UserPropertySanitizer(BaseModelSanitizer):
    model = UserProperty
    field_sanitizers = {
        'value': SmartStringSanitizer(),
    }


ModelSanitizerManager.register(TaskSanitizer())
ModelSanitizerManager.register(UserSanitizer())
ModelSanitizerManager.register(UserPropertySanitizer())
