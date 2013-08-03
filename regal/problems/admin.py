# -*- coding: utf-8 -*-
from django.contrib import admin
from regal.problems.models import *
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

def editButton(obj):
    return u'Uprav'
editButton.short_description = ""

def name_to_url(app, parent, obj):
    url = reverse('admin:%s_%s_changelist' % (app, parent))
    url += 'details/%s' % (obj.id)
    return '<b><a href="%s">%s</a></b>' % (url, obj.__unicode__())

class TaskAdmin(admin.ModelAdmin):
    list_display = ('number','name_to_url', editButton)
    list_display_links = (editButton,)
    ordering = ('number',)

    def get_urls(self):
        urls = super(TaskAdmin, self).get_urls()
        my_urls = patterns('', (r'details/(\d+)$', self.admin_site.admin_view(self.review)),)
        return my_urls + urls

    def review(self, request, id):
        task = Task.objects.get(pk=id)
        evaulations = Point.objects.all().filter(task=task.id)
        submit_types = []
        solvers = []
        for x in evaulations:
            submit_types.append(x.submit_type)
            solvers.append(x.person)
        submit_types = list(set(submit_types))
        solvers = list(set(solvers))
        results = {}
        for x in solvers:
            results[x.__unicode__()] = {}
            for y in submit_types:
                results[x.__unicode__()][y] = 0
        for x in evaulations:
            results[x.person.__unicode__()][x.submit_type] = x.points

        return render_to_response('admin/problems/task_details.html',
        {},
        context_instance=RequestContext(request))
    
    def name_to_url(self, obj):
        return name_to_url('problems', 'task', obj)
    name_to_url.short_description = u'Názov'
    name_to_url.allow_tags = True

class PointAdmin(admin.ModelAdmin):
    list_display = ['person', 'submit_type', 'points', editButton]
    list_display_links = (editButton,)

admin.site.register(Task,TaskAdmin)
admin.site.register(Point,PointAdmin)
