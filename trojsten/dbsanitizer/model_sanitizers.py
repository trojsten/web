# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

from bulk_update.helper import bulk_update

from trojsten.regal.tasks.models import Task


class BaseFieldSnatizer(object):
    def sanitize(self, data):
        return data


class GeneratorSanitizer(BaseFieldSnatizer):
    def generate(self):
        return None

    def sanitize(self, data):
        return self.generate()


class TaskNameSanitizer(GeneratorSanitizer):
    def generate(self):
        alphabet = 'qwertyuiopasdfghjklzxcvbnm'*3 + 'äřéŕťýúíóôášďěüöůĺľžčň' + '     '
        return ''.join(random.choice(alphabet) for _ in range(random.randrange(5, 20)))


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
        'name': TaskNameSanitizer(),
    }
