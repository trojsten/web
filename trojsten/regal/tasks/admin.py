# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.encoding import force_text

from easy_select2 import select2_modelform

from trojsten.regal.tasks.models import *
from trojsten.regal.tasks.forms import TaskValidationForm
from trojsten.regal.utils import get_related, attribute_format
from trojsten.reviews.urls import task_review_urls, submit_urls


class TaskByYearSubFilter(admin.SimpleListFilter):
    '''
    Shows only lookups of years for chosen competition.
    '''
    title = 'ročník'
    parameter_name = 'year_subfilter'

    def lookups(self, request, model_admin):
        tasks = Task.objects
        if 'round__series__competition__id__exact' in request.GET:
            tasks = tasks.filter(round__series__competition__id__exact=request.GET['round__series__competition__id__exact'])
        tasks = tasks.select_related('round__series__year')
        tasks = tasks.distinct('round__series__year').order_by('-round__series__year')
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
        if 'round__series__competition__id__exact' in request.GET:
            tasks = tasks.filter(round__series__competition__id__exact=request.GET['round__series__competition__id__exact'])
        if 'year_subfilter' in request.GET:
            tasks = tasks.filter(round__series__year=request.GET['year_subfilter'])
        tasks = tasks.select_related('round__series__competition')
        tasks = tasks.distinct('round__series__competition',
                               'round__series__year', 'round__series__number', 'round__number')
        tasks = tasks.order_by('round__series__competition',
                               '-round__series__year', '-round__series__number', '-round__number')
        rounds = (x.round for x in tasks.all())
        return ((r.id, force_text(r)) for r in rounds)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(round__id__exact=self.value())
        else:
            return queryset


class TaskAdmin(admin.ModelAdmin):
    change_form_template = 'admin/task_review.html'
    form = select2_modelform(Task, form_class=TaskValidationForm)

    list_select_related = True
    list_display = ('name', 'number',
                    'get_round', 'get_series', 'get_year', 'get_competition', 'get_category',
                    'submit_type', 'integer_source_points', 'reviewer',
                    'tasks_pdf', 'solutions_pdf')
    list_filter = ('round__series__competition', TaskByYearSubFilter, TaskByRoundSubFilter)
    search_fields = ('name',)

    get_round = get_related(attribute_chain=('round', 'short_str'),
                            description='kolo',
                            order='round__number')
    get_series = get_related(attribute_chain=('round', 'series', 'short_str'),
                             description='séria',
                             order='round__series__number')
    get_year = get_related(attribute_chain=('round', 'series', 'year'),
                           description='ročník',
                           order='round__series__year')
    get_competition = get_related(attribute_chain=('round', 'series', 'competition'),
                                  description='súťaž',
                                  order='round__series__competition')

    def get_urls(self):
        return task_review_urls + super(TaskAdmin, self).get_urls()

    def get_category(self, obj):
        return ', '.join(force_text(x.name) for x in obj.category.all())
    get_category.short_description = 'kategória'
    get_category.admin_order_field = 'category'

    def submit_type(self, obj):
        res = ''
        if obj.has_description:
            res += 'popis:%i ' % obj.description_points
        if obj.has_source:
            res += 'kód:%i ' % obj.source_points
        if obj.has_testablezip:
            res += 'zip '
        if bool(obj.external_submit_link):
            res += 'link: %s' % obj.external_submit_link
        return res
    submit_type.short_description = 'odovzdávanie a bodovanie'

    tasks_pdf = attribute_format(attribute='task_file_exists',
                                 description='zadanie',
                                 boolean=True)
    solutions_pdf = attribute_format(attribute='solution_file_exists',
                                     description='vzorák',
                                     boolean=True)

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        round_lst = Round.objects.filter(series__competition__organizers_group__in=user_groups)
        return super(TaskAdmin, self).get_queryset(request).filter(
            round__in=round_lst
        ).distinct().prefetch_related('category').select_related('reviewer', 'round__series__competition')


class SubmitAdmin(admin.ModelAdmin):
    change_form_template = 'admin/submit_form.html'
    form = select2_modelform(Submit)

    list_select_related = True
    list_display = ('get_task_name', 'get_task_number',
                    'get_round', 'get_series', 'get_year', 'get_competition', 'get_category',
                    'user', 'time', 'get_points', 'submit_type', 'testing_status', 'filepath',)
    list_filter = ('task__round__series__competition',)
    search_fields = ('user__username', 'task__name',)

    get_points = attribute_format(
        attribute='user_points',
        description='body',
    )

    get_task_name = get_related(attribute_chain=('task', 'name'),
                                description='úloha',
                                order='task__name')
    get_task_number = get_related(attribute_chain=('task', 'number'),
                                  description='č.ú.',
                                  order='task__number')
    get_round = get_related(attribute_chain=('task', 'round', 'short_str'),
                            description='kolo',
                            order='task__round__number')
    get_series = get_related(attribute_chain=('task', 'round', 'series', 'short_str'),
                             description='séria',
                             order='task__round__series__number')
    get_year = get_related(attribute_chain=('task', 'round', 'series', 'year'),
                           description='ročník',
                           order='task__round__series__year')
    get_competition = get_related(attribute_chain=('task', 'round', 'series', 'competition'),
                                  description='súťaž',
                                  order='task__round__series__competition')

    def get_urls(self):
        return submit_urls + super(SubmitAdmin, self).get_urls()

    def get_category(self, obj):
        return ', '.join(force_text(x.name) for x in obj.task.category.all())
    get_category.short_description = 'kategória'
    get_category.admin_order_field = 'task__category'

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        round_lst = Round.objects.filter(series__competition__organizers_group__in=user_groups)
        task_lst = Task.objects.filter(round__in=round_lst)
        return super(SubmitAdmin, self).get_queryset(request).filter(
            task__in=task_lst
        ).prefetch_related('task__category')


class CategoryAdmin(admin.ModelAdmin):
    form = select2_modelform(Category)
    list_filter = ('competition',)

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        return super(CategoryAdmin, self).get_queryset(request).filter(
            competition__organizers_group__in=user_groups
        ).select_related('competition')


admin.site.register(Task, TaskAdmin)
admin.site.register(Submit, SubmitAdmin)
admin.site.register(Category, CategoryAdmin)
