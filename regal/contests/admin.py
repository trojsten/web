# -*- coding: utf-8 -*-
from django.contrib import admin
from regal.contests.models import *
from django.core.urlresolvers import reverse

def edit(obj):
    return "Edit"
edit.short_description = ""

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name_to_url',edit)
    list_display_links = (edit,)
    ordering = ('name',)

    def name_to_url(self,obj):
        url = reverse('admin:%s_%s_changelist' % ('contests','year'))
        url += '?contest__id__exact=%s' % (obj.id)
        return '<a href="%s">%s</a>' % (url,obj.name)
    name_to_url.short_description = "Názov"
    name_to_url.allow_tags = True

class YearAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'year', edit)
    list_display_links = (edit,)
    ordering = ('-year',)

admin.site.register(Competition,CompetitionAdmin)
admin.site.register(Year,YearAdmin)
admin.site.register(Round)
admin.site.register(Task)
