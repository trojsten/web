# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from regal.people.models import *

admin.site.register(Address)
admin.site.register(Person)
