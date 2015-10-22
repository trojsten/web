# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.encoding import force_text

from easy_select2 import select2_modelform

from trojsten.regal.contests.models import *
from trojsten.regal.utils import get_related, attribute_format


class CompetitionAdmin(admin.ModelAdmin):
    form = select2_modelform(Competition)
    list_display = ('name', 'organizers_group', 'get_sites', 'repo', 'repo_root')

    def get_sites(self, obj):
        return ', '.join(force_text(x) for x in obj.sites.all())
    get_sites.short_description = 'doména súťaže'


class SeriesAdmin(admin.ModelAdmin):
    form = select2_modelform(Series)
    list_display = ('short_str', 'number', 'name', 'competition', 'year')
    list_filter = ('competition', 'year')


class RoundAdmin(admin.ModelAdmin):
    form = select2_modelform(Round)
    list_select_related = True
    list_display = ('short_str',
                    'get_series_number', 'get_series_name', 'get_year', 'get_competition',
                    'can_submit', 'start_time', 'end_time',
                    'visible', 'tasks_pdf',
                    'solutions_visible', 'solutions_pdf')
    list_filter = ('series__competition', 'series__year')

    get_series_number = get_related(attribute_chain=('series', 'number'),
                                    description='séria',
                                    order='series__number')
    get_series_name = get_related(attribute_chain=('series', 'name'),
                                  description='názov série',
                                  order='series__name')
    get_year = get_related(attribute_chain=('series', 'year'),
                           description='ročník',
                           order='series__year')
    get_competition = get_related(attribute_chain=('series', 'competition'),
                                  description='súťaž',
                                  order='series__competition')

    tasks_pdf = attribute_format(attribute='tasks_pdf_exists',
                                 description='zadania v pdf',
                                 boolean=True)
    solutions_pdf = attribute_format(attribute='solutions_pdf_exists',
                                     description='vzoráky v pdf',
                                     boolean=True)
    can_submit = attribute_format(attribute='can_submit',
                                  description='prebieha',
                                  boolean=True)

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        competition_lst = Competition.objects.filter(organizers_group__in=user_groups)
        series_lst = Series.objects.filter(competition__in=competition_lst)
        return super(RoundAdmin, self).get_queryset(request).filter(
            series__in=series_lst
        )


class RepositoryAdmin(admin.ModelAdmin):
    readonly_fields = ('notification_string',)

admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Repository, RepositoryAdmin)
