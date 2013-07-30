    # -*- coding: utf-8 -*-
from django.contrib import admin
from regal.contests.models import *
from django.core.urlresolvers import reverse
from regal.contests.models import Year

# maybe we will need this:
#class YearInline(admin.TabularInline):
#    model = Year
#    can_delete = False
#    fk_name = 'competition'
#    fields = ('number', 'year')
    
def editButton(obj):
    return u'Uprav'
editButton.short_description = ""

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name_to_url','newest_year',editButton)
    list_display_links = (editButton,)
    ordering = ('name',)

    def name_to_url(self,obj):
        url = reverse('admin:%s_%s_changelist' % ('contests','year'))
        url += '?competition__id=%s' % (obj.id)
        return '<b><a href="%s">%s</a></b>' % (url, obj.name)
    name_to_url.short_description = u'Názov'
    name_to_url.allow_tags = True
    
    def newest_year(self, obj):
        year = Year.objects.filter(competition=obj.id).order_by('-year')[:1]
        url = reverse('admin:%s_%s_changelist' % ('contests','round'))
        url += '?year__id=%s' % (year[0].id)
        return '<b><a href="%s">%s</a></b>' % (url, year[0].__unicode__())
    newest_year.short_description = u'Najnovší ročník'
    newest_year.allow_tags = True

    fields = ('name', ('informatics', 'math', 'physics'), )
#   maybe we will need this:
#    inlines = [
#        YearInline, 
#    ]

class YearAdmin(admin.ModelAdmin):
    list_display = ('name_to_url', 'year', editButton)
    list_display_links = (editButton,)
    ordering = ('-year',)
    
    def name_to_url(self, obj):
        url = reverse('admin:%s_%s_changelist' % ('contests','round'))
        url += '?year__id=%s' % (obj.id)
        return '<b><a href="%s">%s</a></b>' % (url, obj.__unicode__())
    name_to_url.short_description = u'Názov'
    name_to_url.allow_tags = True

class RoundAdmin(admin.ModelAdmin):
    list_display = ('name_to_url', editButton)
    list_display_links = (editButton,)

    def name_to_url(self, obj):
        url = reverse('admin:%s_%s_changelist' % ('contests','task'))
        url += '?in_round__id=%s' % (obj.id)
        print url
        return '<b><a href="%s">%s</a></b>' % (url, obj.__unicode__())
    name_to_url.short_description = u'Názov'
    name_to_url.allow_tags = True

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', editButton)
    list_display_links = (editButton,)

admin.site.register(Competition,CompetitionAdmin)
admin.site.register(Year,YearAdmin)
admin.site.register(Round,RoundAdmin)
admin.site.register(Task,TaskAdmin)
