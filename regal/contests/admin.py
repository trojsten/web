# -*- coding: utf-8 -*-
from django.contrib import admin
from regal.contests.models import *
from django.core.urlresolvers import reverse
from datetime import date
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

def name_to_url(parent, son, obj):
    url = reverse('admin:%s_%s_changelist' % ('contests',son))
    url += '?%s__id=%s' % (parent, obj.id)
    return '<b><a href="%s">%s</a></b>' % (url, obj.__unicode__())
#name_to_url.short_description = u'Názov'
#name_to_url.allow_tags = True
    

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name_to_url','newest_year',editButton)
    list_display_links = (editButton,)
    ordering = ('name',)
    
    def name_to_url(self,obj):
        return name_to_url('competition','year', obj)
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
    list_filter = ('competition',)

    ordering = ('-year',)
    
    def name_to_url(self, obj):
        return name_to_url('year','round', obj)
    name_to_url.short_description = u'Názov'
    name_to_url.allow_tags = True

    def add_view(self, request, form_url="", extra_context=None):
        ''' predefined values in add_view form 
        '''
        data = request.GET.copy()
        c_id = request.GET.get('competition', False)
        if c_id:
            form_url = '?competition='+c_id
            c = Competition.objects.get(id=c_id)
            data['number'] = Year.objects.filter(competition=c).count()+1
        data['year'] = date.today().year        
        request.GET = data
        return super(YearAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        c_id = request.GET.get('competition__id', False)
        if c_id:
            extra_context['add_options'] = 'competition='+c_id
            c = Competition.objects.get(id=c_id)
            extra_context['title'] = u'Vybrať "'+Year._meta.verbose_name+'" z "'+c.__unicode__()+'"'
        return super(YearAdmin, self).changelist_view(request, extra_context=extra_context)

class RoundAdmin(admin.ModelAdmin):
    list_display = ('name_to_url', 'end_time', editButton)
    list_display_links = (editButton,)
    list_filter = ('end_time',)
    ordering = ('number',)

    def name_to_url(self, obj):
        return name_to_url('in_round','task', obj)
    name_to_url.short_description = u'Názov'
    name_to_url.allow_tags = True
    
    def add_view(self, request, form_url="", extra_context=None):
        ''' predefined values in add_view form
        '''
        data = request.GET.copy()
        y_id = request.GET.get('year', False)
        if y_id:
            y = Year.objects.get(id=y_id)
            data['number'] = Round.objects.filter(year=y).count()+1
        
        request.GET = data
        return super(RoundAdmin, self).add_view(request, form_url="", extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        y_id = request.GET.get('year__id', False)
        if y_id:
            extra_context['add_options'] = 'year='+y_id
            y = Year.objects.get(id=y_id)
            extra_context['title'] = u'Vybrať "'+Round._meta.verbose_name+'" z "'+y.__unicode__()+'"'
        return super(RoundAdmin, self).changelist_view(request, extra_context=extra_context)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('number','name', editButton)
    list_display_links = (editButton,)
    ordering = ('number',)

admin.site.register(Competition,CompetitionAdmin)
admin.site.register(Year,YearAdmin)
admin.site.register(Round,RoundAdmin)
admin.site.register(Task, TaskAdmin)
