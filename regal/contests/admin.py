    # -*- coding: utf-8 -*-
from django.contrib import admin
from regal.contests.models import *
from django.core.urlresolvers import reverse
<<<<<<< HEAD
from datetime import date
=======
from regal.contests.models import Year
>>>>>>> ae448a827f6c9bd0d4f6a894337fee8bd49268ec

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

    def add_view(self, request, form_url="", extra_context=None):
        ''' predefined values in add_view form 
        '''
        data = request.GET.copy()
        c_id = request.GET.get('competition', False)
        if c_id:
            c = Competition.objects.get(id=c_id)
            data['number'] = Year.objects.filter(competition=c).count()+1
        data['year'] = date.today().year      
        
        request.GET = data
        return super(YearAdmin, self).add_view(request, form_url="", extra_context=extra_context)

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
