# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import date

from django.contrib import admin
from django.core.urlresolvers import reverse

from regal.problems.models import *
from regal.contests.models import *

def editButton(obj):
    return 'Uprav'
editButton.short_description = ""


def name_to_url(app, parent, son, obj):
    url = reverse('admin:%s_%s_changelist' % (app, son))
    url += '?%s__id__exact=%s' % (parent, obj.id)
    return '<b><a href="%s">%s</a></b>' % (url, obj.__unicode__())
#name_to_url.short_description = 'Názov'
#name_to_url.allow_tags = True


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name_to_url', 'newest_series', editButton)
    list_display_links = (editButton,)
    ordering = ('name',)

    def name_to_url(self, obj):
        return name_to_url('contests', 'competition', 'series', obj)
    name_to_url.short_description = 'Názov'
    name_to_url.allow_tags = True

    def newest_series(self, obj):
        series = Series.objects.filter(competition=obj.id).latest('start_date')
        url = reverse('admin:%s_%s_changelist' % ('contests', 'round'))
        url += '?series__id__exact=%s' % (series.id)
        return '<b><a href="%s">%s</a></b>' % (url, series.__unicode__())
    newest_series.short_description = 'Najnovšia séria'
    newest_series.allow_tags = True

    fields = ('name', ('informatics', 'math', 'physics'), )


class SeriesAdmin(admin.ModelAdmin):
    list_display = ('name_to_url', 'start_date', editButton)
    list_display_links = (editButton,)
    list_filter = ('competition',)

    ordering = ('-start_date',)

    def name_to_url(self, obj):
        return name_to_url('contests', 'series', 'round', obj)
    name_to_url.short_description = 'Názov'
    name_to_url.allow_tags = True

    def add_view(self, request, form_url="", extra_context=None):
        """
        predefined values in add_view form
        """
        data = request.GET.copy()
        c_id = request.GET.get('competition', False)
        if c_id:
            form_url = '?competition=' + c_id
            c = Competition.objects.get(id=c_id)
            data['number'] = Series.objects.filter(competition=c).count() + 1
        data['start_date'] = date.today()
        request.GET = data
        return super(SeriesAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        c_id = request.GET.get('competition__id__exact', False)
        if c_id:
            extra_context['add_options'] = 'competition=' + c_id
            c = Competition.objects.get(id=c_id)
            extra_context['title'] = 'Vybrať %s z %s' % (Series._meta.verbose_name, c.__unicode__())
        return super(SeriesAdmin, self).changelist_view(request, extra_context=extra_context)


class RoundAdmin(admin.ModelAdmin):
    list_display = ('name_to_url', 'end_time', editButton)
    list_display_links = (editButton,)
    list_filter = ('end_time',)
    ordering = ('number',)

    def name_to_url(self, obj):
        return name_to_url('problems', 'in_round', 'task', obj)
    name_to_url.short_description = 'Názov'
    name_to_url.allow_tags = True

    def add_view(self, request, form_url="", extra_context=None):
        """
        predefined values in add_view form
        """
        data = request.GET.copy()
        s_id = request.GET.get('series', False)
        if s_id:
            s = Series.objects.get(id=s_id)
            data['number'] = Round.objects.filter(series=s).count() + 1

        request.GET = data
        return super(RoundAdmin, self).add_view(request, form_url="", extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        s_id = request.GET.get('series__id__exact', False)
        if s_id:
            extra_context['add_options'] = 'series=' + s_id
            s = Series.objects.get(id=s_id)
            extra_context['title'] = 'Vybrať %s z %s' % (Round._meta.verbose_name, s.__unicode__())
        return super(RoundAdmin, self).changelist_view(request, extra_context=extra_context)


admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Round, RoundAdmin)
