# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

from bulk_update.helper import bulk_update

from trojsten.regal.tasks.models import Task


class BaseFieldSantizer(object):
    def sanitize(self, data):
        return data


class GeneratorFieldSanitizer(BaseFieldSantizer):
    def __init__(self, generator):
        self.generator = generator

    def sanitize(self, data):
        return self.generator.generate()


class TaskNameGenerator(object):
    def generate(self):
        alphabet = 'qwertyuiopasdfghjklzxcvbnm'*3 + 'äřéŕťýúíóôášďěüöůĺľžčň' + '     '
        return ''.join(random.choice(alphabet) for _ in range(random.randrange(5, 20)))


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
        'name': GeneratorFieldSanitizer(TaskNameGenerator()),
    }

ModelSanitizerManager.register(TaskSanitizer())
