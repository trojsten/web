# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from trojsten.regal.people.models import *

admin.site.register(Address)
admin.site.register(School)
admin.site.register(User)
