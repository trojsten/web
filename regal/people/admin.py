# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from regal.people.models import *


def create_alphabet_filter(field, requestget):
    kw = '__startswith'
    selected_choice = requestget.get(field + kw, 'All')
    choices = [{'title': 'All',
                'link': '?',
                'active': selected_choice == 'All'}]
    for x in range(26):
        letter = chr(ord('A') + x)
        choices.append({'title': letter,
                        'link': '?%s%s=%s' % (field, kw, letter),
                        'active': selected_choice == letter})
    return choices


class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'surname', 'email')
    list_filter = ['studies_in', 'teaches_in']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['choices'] = create_alphabet_filter('surname',
                                                          request.GET)
        return super(PersonAdmin,
                     self).changelist_view(request,
                                           extra_context=extra_context)


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('abbr', 'name', 'address', 'get_town')


admin.site.register(Address)
admin.site.register(Person, PersonAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
