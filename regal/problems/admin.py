# -*- coding: utf-8 -*-
from django.contrib import admin
from regal.problems.models import *

def editButton(obj):
    return u'Uprav'
editButton.short_description = ""

class TaskAdmin(admin.ModelAdmin):
    list_display = ('number','name', editButton)
    list_display_links = (editButton,)
    ordering = ('number',)

admin.site.register(Task,TaskAdmin)
admin.site.register(Point)
