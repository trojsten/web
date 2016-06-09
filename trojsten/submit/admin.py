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

admin.site.register(Submit, SubmitAdmin)
