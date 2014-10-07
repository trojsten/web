# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.encoding import force_text

from trojsten.regal.tasks.models import *
from trojsten.regal.utils import get_related, attribute_format


class TaskByYearSubFilter(admin.SimpleListFilter):
    '''
    Shows only lookups of years for chosen competition.
    '''
    title = 'ročník'
    parameter_name = 'year_subfilter'

    def lookups(self, request, model_admin):
        tasks = Task.objects
        if 'category__competition__id__exact' in request.GET:
            tasks = tasks.filter(category__competition__id__exact=request.GET['category__competition__id__exact'])
        tasks = tasks.select_related('round__series__year').distinct('round__series__year').order_by('-round__series__year')
        years = (x.round.series.year for x in tasks.all())
        return ((y, force_text(y)) for y in years)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(round__series__year=self.value())
        else:
            return queryset


class TaskByRoundSubFilter(admin.SimpleListFilter):
    '''
    Shows only lookups of rounds for chosen competition and year.
    '''
    title = 'kolo'
    parameter_name = 'round_subfilter'

    def lookups(self, request, model_admin):
        tasks = Task.objects
        if 'category__competition__id__exact' in request.GET:
            tasks = tasks.filter(category__competition__id__exact=request.GET['category__competition__id__exact'])
        if 'year_subfilter' in request.GET:
            tasks = tasks.filter(round__series__year=request.GET['year_subfilter'])
        tasks = tasks.select_related('round__series__competition')
        tasks = tasks.distinct('round__series__competition', 'round__series__year', 'round__series__number', 'round__number')
        tasks = tasks.order_by('round__series__competition', '-round__series__year', '-round__series__number', '-round__number')
        rounds = (x.round for x in tasks.all())
        return ((r.id, force_text(r)) for r in rounds)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(round__id__exact=self.value())
        else:
            return queryset


class TaskAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ('name', 'number',
                    'get_round', 'get_series', 'get_year', 'get_category',
                    'submit_type',
                    'tasks_pdf', 'solutions_pdf')
    list_filter = ('category__competition', TaskByYearSubFilter, TaskByRoundSubFilter)
    search_fields = ('name',)

    get_round = get_related(attribute=('round', 'short_str'), description="kolo", order='round__number')
    get_series = get_related(attribute=('round', 'series', 'short_str'), description="séria", order='round__series__number')
    get_year = get_related(attribute=('round', 'series', 'year'), description="ročník", order='round__series__year')

    def get_category(self, obj):
        return ", ".join(force_text(x) for x in obj.category.all())
    get_category.short_description = 'kategória'

    def submit_type(self, obj):
        res = ""
        if obj.has_description:
            res += "popis:%i " % obj.description_points
        if obj.has_source:
            res += "kód:%i " % obj.source_points
        if obj.has_testablezip:
            res += "zip "
        if bool(obj.external_submit_link):
            res += "link:" + obj.external_submit_link
        return res
    submit_type.short_description = 'odovzdávanie a bodovanie'

    tasks_pdf = attribute_format(attribute='task_file_exists', description="zadanie", boolean=True)
    solutions_pdf = attribute_format(attribute='solution_file_exists', description="vzorák", boolean=True)


class SubmitAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ('get_task_name', 'get_task_number',
                    'get_round', 'get_series', 'get_year', 'get_category',
                    'user', 'submit_type', 'testing_status', 'points', 'filepath', 'time')
    list_filter = ('task__category__competition',)
    search_fields = ('user__username', 'task__name',)

    get_task_name = get_related(attribute=('task', 'name'), description="úloha", order='task__name')
    get_task_number = get_related(attribute=('task', 'number'), description="č. úlohy", order='task__number')

    get_round = get_related(attribute=('task', 'round', 'short_str'), description="kolo", order='task__round__number')
    get_series = get_related(attribute=('task', 'round', 'series', 'short_str'), description="séria", order='task__round__series__number')
    get_year = get_related(attribute=('task', 'round', 'series', 'year'), description="ročník", order='task__round__series__year')

    def get_category(self, obj):
        return ", ".join(force_text(x) for x in obj.task.category.all())
    get_category.short_description = 'kategória'


class CategoryAdmin(admin.ModelAdmin):
    list_filter = ('competition',)

admin.site.register(Task, TaskAdmin)
admin.site.register(Submit, SubmitAdmin)
admin.site.register(Category, CategoryAdmin)
