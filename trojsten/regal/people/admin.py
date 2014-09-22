# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from trojsten.regal.people.models import *


class UserPropertyInLine(admin.TabularInline):
    model = UserProperty
    extra = 0


class UserAdmin(DefaultUserAdmin):
    def __init__(self, *args, **kwargs):
        super(UserAdmin, self).__init__(*args, **kwargs)
        self.fieldsets += (('Extra', {'fields': ('gender', 'birth_date', 'home_address', 'mailing_address', 'school', 'graduation')}),)
        self.inlines = [UserPropertyInLine]

admin.site.register(Address)
admin.site.register(School)
admin.site.register(User, UserAdmin)
