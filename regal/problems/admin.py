# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from regal.problems.models import *


def edit_button(obj):
    return 'Uprav'
edit_button.short_description = ""


def name_to_url(app, parent, obj):
    url = reverse('admin:%s_%s_changelist' % (app, parent))
    url += 'details/%s' % (obj.id)
    return '<b><a href="%s">%s</a></b>' % (url, obj.__unicode__())


class TaskAdmin(admin.ModelAdmin):
    list_display = ('number', 'name_to_url', edit_button)
    list_display_links = (edit_button,)
    ordering = ('number',)

    def get_urls(self):
        urls = super(TaskAdmin, self).get_urls()
        my_urls = patterns(
            '', (r'details/(\d+)$', self.admin_site.admin_view(self.review)),)
        return my_urls + urls

    def review(self, request, id):
        task = Task.objects.get(pk=id)
        evaulations = Evaluation.objects.all().filter(task=task.id)
        submit_types = []
        solvers = []
        for x in evaulations:
            submit_types.append(x.submit_type)
            solvers.append(x.person)
        submit_types = list(set(submit_types))
        submit_types.append('súčet')
        solvers = list(set(solvers))
        results = {}
        for x in solvers:
            results[x.__unicode__()] = {}
            for y in submit_types:
                results[x.__unicode__()][y] = 0
        for x in evaulations:
            results[x.person.__unicode__()][x.submit_type] = x.points
            results[x.person.__unicode__()]['súčet'] += int(x.points)

        return render_to_response('admin/problems/task_details.html',
                                  {'name': task.__unicode__(),
                                   'submit_types': submit_types,
                                   'results': results,
                                   },
                                  context_instance=RequestContext(request))

    def name_to_url(self, obj):
        return name_to_url('problems', 'task', obj)
    name_to_url.short_description = 'Názov'
    name_to_url.allow_tags = True


class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['person', 'submit_type', 'points', edit_button]
    list_display_links = (edit_button,)

admin.site.register(Task, TaskAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
