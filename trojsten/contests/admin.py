# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.encoding import force_text
from easy_select2 import select2_modelform

from trojsten.contests.models import Category, Competition, Round, Semester, Task, TaskPeople
from trojsten.reviews.urls import task_review_urls
from trojsten.contests.forms import TaskValidationForm
from trojsten.utils.utils import attribute_format, get_related


class CompetitionAdmin(admin.ModelAdmin):
    form = select2_modelform(Competition)
    list_display = ('name', 'organizers_group', 'get_sites')

    def get_sites(self, obj):
        return ', '.join(force_text(x) for x in obj.sites.all())
    get_sites.short_description = 'doména súťaže'


class SemesterAdmin(admin.ModelAdmin):
    form = select2_modelform(Semester)
    list_display = ('short_str', 'number', 'name', 'competition', 'year')
    list_filter = ('competition', 'year')


class RoundAdmin(admin.ModelAdmin):
    form = select2_modelform(Round)
    list_select_related = True
    list_display = ('short_str',
                    'get_semester_number', 'get_semester_name', 'get_year', 'get_competition',
                    'can_submit', 'start_time', 'end_time',
                    'visible', 'tasks_pdf',
                    'solutions_visible', 'solutions_pdf')
    list_filter = ('semester__competition', 'semester__year')

    get_semester_number = get_related(attribute_chain=('semester', 'number'),
                                      description='časť',
                                      order='semester__number')
    get_semester_name = get_related(attribute_chain=('semester', 'name'),
                                    description='názov časti',
                                    order='semester__name')
    get_year = get_related(attribute_chain=('semester', 'year'),
                           description='ročník',
                           order='semester__year')
    get_competition = get_related(attribute_chain=('semester', 'competition'),
                                  description='súťaž',
                                  order='semester__competition')

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
        competition_lst = Competition.objects.filter(
            organizers_group__in=user_groups)
        semester_lst = Semester.objects.filter(competition__in=competition_lst)
        return super(RoundAdmin, self).get_queryset(request).filter(
            semester__in=semester_lst
        )


class TaskByYearSubFilter(admin.SimpleListFilter):
    """
    Shows only lookups of years for chosen competition.
    """
    title = 'ročník'
    parameter_name = 'year_subfilter'

    def lookups(self, request, model_admin):
        tasks = Task.objects
        if 'round__semester__competition__id__exact' in request.GET:
            tasks = tasks.filter(
                round__semester__competition__id__exact=request.GET[
                    'round__semester__competition__id__exact'
                ]
            )
        tasks = tasks.select_related('round__semester')
        tasks = tasks.distinct('round__semester__year').order_by(
            '-round__semester__year')
        years = (x.round.semester.year for x in tasks.all())
        return ((y, force_text(y)) for y in years)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(round__semester__year=self.value())
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
        if 'round__semester__competition__id__exact' in request.GET:
            tasks = tasks.filter(
                round__semester__competition__id__exact=request.GET[
                    'round__semester__competition__id__exact'
                ]
            )
        if 'year_subfilter' in request.GET:
            tasks = tasks.filter(
                round__semester__year=request.GET['year_subfilter'])
        tasks = tasks.select_related('round__semester__competition')
        tasks = tasks.distinct('round__semester__competition',
                               'round__semester__year', 'round__semester__number', 'round__number')
        tasks = tasks.order_by('round__semester__competition',
                               '-round__semester__year',
                               '-round__semester__number',
                               '-round__number')
        rounds = (x.round for x in tasks.all())
        return ((r.id, force_text(r)) for r in rounds)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(round__id__exact=self.value())
        else:
            return queryset


class TaskPeopleInline(admin.TabularInline):
    model = TaskPeople
    extra = 1


class TaskAdmin(admin.ModelAdmin):
    change_form_template = 'admin/task_review.html'
    form = select2_modelform(Task, form_class=TaskValidationForm)

    list_select_related = True
    list_display = ('name', 'number',
                    'get_round', 'get_semester', 'get_year', 'get_competition', 'get_categories',
                    'submit_type', 'integer_source_points',
                    'tasks_pdf', 'solutions_pdf')
    list_filter = ('round__semester__competition',
                   TaskByYearSubFilter, TaskByRoundSubFilter)
    search_fields = ('name',)
    inlines = [
        TaskPeopleInline,
    ]

    get_round = get_related(attribute_chain=('round', 'short_str'),
                            description='kolo',
                            order='round__number')
    get_semester = get_related(attribute_chain=('round', 'semester', 'short_str'),
                               description='časť',
                               order='round__semester__number')
    get_year = get_related(attribute_chain=('round', 'semester', 'year'),
                           description='ročník',
                           order='round__semester__year')
    get_competition = get_related(attribute_chain=('round', 'semester', 'competition'),
                                  description='súťaž',
                                  order='round__semester__competition')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user_groups = request.user.groups.all()
        if db_field.name == 'round':
            kwargs['queryset'] = Round.objects.filter(
                semester__competition__organizers_group__in=user_groups
            ).order_by('-end_time')
        return super(TaskAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        return task_review_urls + super(TaskAdmin, self).get_urls()

    def get_categories(self, obj):
        return ', '.join(force_text(x.name) for x in obj.categories.all())
    get_categories.short_description = 'kategória'
    get_categories.admin_order_field = 'categories'

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
        round_lst = Round.objects.filter(
            semester__competition__organizers_group__in=user_groups)
        return super(TaskAdmin, self).get_queryset(request).filter(
            round__in=round_lst
        ).distinct().prefetch_related('categories').select_related(
            'round__semester__competition'
        )


class CategoryAdmin(admin.ModelAdmin):
    form = select2_modelform(Category)
    list_filter = ('competition',)

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        return super(CategoryAdmin, self).get_queryset(request).filter(
            competition__organizers_group__in=user_groups
        ).select_related('competition')


admin.site.register(Task, TaskAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Round, RoundAdmin)
