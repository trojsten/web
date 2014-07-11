# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from trojsten.regal.tasks.models import *

admin.site.register(Task)
admin.site.register(Submit)
admin.site.register(Category)
