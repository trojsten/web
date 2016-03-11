# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

from bulk_update.helper import bulk_update

from trojsten.regal.tasks.models import Task


class BaseFieldSnatizer(object):
    def santize(self, data):
        return data


class GeneratorSantizer(BaseFieldSnatizer):
    def generate(self):
        return None

    def santize(self, data):
        return self.generate()


class TaskNameSantizer(GeneratorSantizer):
    def generate(self):
        alphabet = 'qwertyuiopasdfghjklzxcvbnm'*3 + 'äřéŕťýúíóôášďěüöůĺľžčň' + '     '
        return ''.join(random.choice(alphabet) for _ in range(random.randrange(5, 20)))


class BaseModelSantizer(object):
    model = None
    field_santizers = dict()

    def get_objects(self):
        return self.model.objects.all()

    def santize_single_object(self, obj, save=False):
        for field, field_santizer in self.field_santizers.items():
            setattr(obj, field, field_santizer.santize(getattr(obj, field)))
        if save:
            obj.save()
        return obj

    def santize(self):
        objects = self.get_objects()
        for obj in objects:
            self.santize_single_object(obj)
        bulk_update(objects, update_fields=self.field_santizers.keys())


class TaskSantizer(BaseModelSantizer):
    model = Task
    field_santizers = {
        'name': TaskNameSantizer(),
    }
