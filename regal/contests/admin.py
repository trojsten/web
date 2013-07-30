    # -*- coding: utf-8 -*-
from django.contrib import admin
from regal.contests.models import *
from django.core.urlresolvers import reverse

class YearInline(admin.TabularInline):
    model = Year
    can_delete = False
    fk_name = 'competition'
    fields = ('number', 'year')
    
def editButton(obj):
    return "Edit"
editButton.short_description = ""

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name_to_url',editButton)
    list_display_links = (editButton,)
    ordering = ('name',)

    def name_to_url(self,obj):
        url = reverse('admin:%s_%s_changelist' % ('contests','year'))
        url += '?competition__id__exact=%s' % (obj.id)
        return '<a href="%s">%s</a>' % (url,obj.name)
    name_to_url.short_description = "Názov"
    name_to_url.allow_tags = True
    
    fields = ('name', ('informatics', 'math', 'physics'), )
    inlines = [
        YearInline, 
    ]

class YearAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'year', editButton)
    list_display_links = (editButton,)
    ordering = ('-year',)

admin.site.register(Competition,CompetitionAdmin)
admin.site.register(Year,YearAdmin)
admin.site.register(Round)
admin.site.register(Task)
