# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from trojsten.regal.contests.models import *

class RepositoryAdmin(admin.ModelAdmin):
    readonly_fields=('notification_string',)

admin.site.register(Competition)
admin.site.register(Series)
admin.site.register(Round)
admin.site.register(Repository, RepositoryAdmin)
