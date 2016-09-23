# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.encoding import force_text
from easy_select2 import select2_modelform

from trojsten.contests.models import Round
from trojsten.reviews.urls import submit_urls
from trojsten.contests.models import Task
from trojsten.utils.utils import attribute_format, get_related

from .models import Submit


class SubmitAdmin(admin.ModelAdmin):
    change_form_template = 'admin/submit_form.html'
    form = select2_modelform(Submit)

    list_select_related = True
    list_display = ('get_task_name', 'get_task_number',
                    'get_round', 'get_semester', 'get_year', 'get_competition', 'get_categories',
                    'user', 'time', 'get_points', 'submit_type', 'testing_status', 'filepath',)
    list_filter = ('task__round__semester__competition',)
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
    get_semester = get_related(attribute_chain=('task', 'round', 'semester', 'short_str'),
                               description='časť',
                               order='task__round__semester__number')
    get_year = get_related(attribute_chain=('task', 'round', 'semester', 'year'),
                           description='ročník',
                           order='task__round__semester__year')
    get_competition = get_related(attribute_chain=('task', 'round', 'semester', 'competition'),
                                  description='súťaž',
                                  order='task__round__semester__competition')

    def get_urls(self):
        return submit_urls + super(SubmitAdmin, self).get_urls()

    def get_categories(self, obj):
        return ', '.join(force_text(x.name) for x in obj.task.categories.all())
    get_categories.short_description = 'kategória'
    get_categories.admin_order_field = 'task__categories'

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        round_lst = Round.objects.filter(semester__competition__organizers_group__in=user_groups)
        task_lst = Task.objects.filter(round__in=round_lst)
        return super(SubmitAdmin, self).get_queryset(request).filter(
            task__in=task_lst
        ).prefetch_related('task__categories')

admin.site.register(Submit, SubmitAdmin)
