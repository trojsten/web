# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.encoding import force_text
from django.utils.html import escape

from trojsten.regal.people.models import *
from trojsten.regal.utils import attribute_format


class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'town', 'postal_code', 'country')
    search_fields = ('street', 'town', 'postal_code', 'country')


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('verbose_name', 'abbreviation', 'addr_name', 'street', 'city', 'zip_code')
    search_fields = ('verbose_name', 'abbreviation', 'addr_name', 'street', 'city', 'zip_code')


class UserPropertyInLine(admin.TabularInline):
    model = UserProperty
    extra = 0


class StaffFilter(admin.SimpleListFilter):
    title = 'postavenia'
    parameter_name = 'is_staff'

    def lookups(self, request, model_admin):
        return (
            ('veduci', 'Vedúci'),
            ('ucastnik', 'Účastník'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'veduci':
            return queryset.filter(is_staff=True)
        elif self.value() == 'ucastnik':
            return queryset.filter(is_staff=False)
        else:
            return queryset


class UserAdmin(DefaultUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'get_school', 'graduation', 'get_is_staff', 'get_groups',
                    'is_active', 'get_properties')
    list_filter = ('groups', StaffFilter)
    search_fields = ('username', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(UserAdmin, self).__init__(*args, **kwargs)
        self.fieldsets += (('Extra', {'fields': ('gender', 'birth_date', 'home_address',
                                                 'mailing_address', 'school', 'graduation')}),)
        self.inlines = (UserPropertyInLine,)

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        return qs.select_related('school').prefetch_related(
            'groups', 'properties__key'
        )

    def get_groups(self, obj):
        return ', '.join(force_text(x) for x in obj.groups.all())
    get_groups.short_description = 'skupiny'

    get_is_staff = attribute_format(attribute='is_staff', description='vedúci', boolean=True)

    def get_school(self, obj):
        if obj.school.has_abbreviation:
            show = obj.school.abbreviation
        else:
            show = obj.school.verbose_name
        return '<span title="%s">%s</span>' % (escape(force_text(obj.school)), escape(force_text(show)))
    get_school.short_description = 'škola'
    get_school.admin_order_field = 'school'
    get_school.allow_tags = True


    def get_properties(self, obj):
        return '<br />'.join(escape(force_text(x)) for x in obj.properties.all())
    get_properties.short_description = 'dodatočné vlastnosti'
    get_properties.allow_tags = True


admin.site.register(Address, AddressAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserPropertyKey)
