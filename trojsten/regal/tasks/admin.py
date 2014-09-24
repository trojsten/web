# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from trojsten.regal.tasks.models import *
from trojsten.regal.contests.models import *


class TaskByYearSubFilter(admin.SimpleListFilter):
    """
    Shows only lookups of years for chosen competition.
    """
    title = 'ročník'
    parameter_name = 'year_subfilter'

    def lookups(self, request, model_admin):
        tasks = Task.objects
        if 'category__competition__id__exact' in request.GET:
            tasks = tasks.filter(category__competition__id__exact=request.GET['category__competition__id__exact'])
        years = set([x.round.series.year for x in tasks.all()])
        return [(y, unicode(y)) for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(round__series__year=self.value())
        else:
            return queryset


class TaskByRoundSubFilter(admin.SimpleListFilter):
    """
    Shows only lookups of rounds for chosen competition and year.
    """
    title = 'kolo'
    parameter_name = 'round_subfilter'

    def lookups(self, request, model_admin):
        tasks = Task.objects
        if 'category__competition__id__exact' in request.GET:
            tasks = tasks.filter(category__competition__id__exact=request.GET['category__competition__id__exact'])
        if 'year_subfilter' in request.GET:
            tasks = tasks.filter(round__series__year=request.GET['year_subfilter'])
        rounds = set([x.round for x in tasks.all()])
        return [(r.id, unicode(r)) for r in rounds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(round__id__exact=self.value())
        else:
            return queryset


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'get_category', 'round',
                    'submit_type',
                    'tasks_pdf', 'solutions_pdf')
    list_filter = ('category__competition', TaskByYearSubFilter, TaskByRoundSubFilter)
    search_fields = ('name',)

    def get_category(self, obj):
        return ", ".join([unicode(x) for x in obj.category.all()])
    get_category.short_description = 'kategória'

    def submit_type(self, obj):
        res = ""
        if obj.has_description:
            res += "popis:" + str(obj.description_points) + " "
        if obj.has_source:
            res += "kód:" + str(obj.source_points) + " "
        if obj.has_testablezip:
            res += "Zip "
        if bool(obj.external_submit_link):
            res += "link:" + obj.external_submit_link
        return res
    submit_type.short_description = 'odovzdávanie a bodovanie'

    def tasks_pdf(self, obj):
        return obj.task_file_exists
    tasks_pdf.short_description = "zadanie"
    tasks_pdf.boolean = True

    def solutions_pdf(self, obj):
        return obj.solution_file_exists
    solutions_pdf.short_description = "vzorák"
    solutions_pdf.boolean = True


class SubmitAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'submit_type', 'testing_status', 'points', 'filepath', 'time')
    list_filter = ('task__category__competition',)
    search_fields = ('user__username', 'task__name',)


class CategoryAdmin(admin.ModelAdmin):
    list_filter = ('competition',)

admin.site.register(Task, TaskAdmin)
admin.site.register(Submit, SubmitAdmin)
admin.site.register(Category, CategoryAdmin)
