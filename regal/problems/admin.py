# -*- coding: utf-8 -*-
from django.contrib import admin
from regal.problems.models import *
from django.core.urlresolvers import reverse

def editButton(obj):
    return u'Uprav'
editButton.short_description = ""

def name_to_url(app, parent, son, obj):
    url = reverse('admin:%s_%s_changelist' % (app, son))
    url += '?%s__id__exact=%s' % (parent, obj.id)
    return '<b><a href="%s">%s</a></b>' % (url, obj.__unicode__())

class TaskAdmin(admin.ModelAdmin):
    list_display = ('number','name_to_url', editButton)
    list_display_links = (editButton,)
    ordering = ('number',)
    
    def name_to_url(self, obj):
        return name_to_url('problems', 'task', 'point', obj)
    name_to_url.short_description = u'Názov'
    name_to_url.allow_tags = True

class PointAdmin(admin.ModelAdmin):
    list_display = ['person', 'submit_type', 'points', editButton]
    list_display_links = (editButton,)

admin.site.register(Task,TaskAdmin)
admin.site.register(Point,PointAdmin)
