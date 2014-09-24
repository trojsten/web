# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from trojsten.regal.contests.models import *


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizers_group', 'get_sites', 'repo', 'repo_root')

    def get_sites(self, obj):
        return ", ".join([unicode(x) for x in obj.sites.all()])
    get_sites.short_description = 'doména súťaže'


class SeriesAdmin(admin.ModelAdmin):
    list_filter = ('competition', 'year')


class RoundAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'can_submit', 'end_time',
                    'visible', 'tasks_pdf',
                    'solutions_visible', 'solutions_pdf')
    list_filter = ('series__competition', 'series__year')

    def tasks_pdf(self, obj):
        return obj.tasks_pdf_exists
    tasks_pdf.short_description = "existujú zadania v pdf"
    tasks_pdf.boolean = True

    def solutions_pdf(self, obj):
        return obj.solutions_pdf_exists
    solutions_pdf.short_description = "existujú vzoráky v pdf"
    solutions_pdf.boolean = True

    def can_submit(self, obj):
        return obj.can_submit
    can_submit.short_description = "prebieha"
    can_submit.boolean = True


class RepositoryAdmin(admin.ModelAdmin):
    readonly_fields = ('notification_string',)

admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Repository, RepositoryAdmin)
