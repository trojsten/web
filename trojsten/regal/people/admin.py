# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from trojsten.regal.people.models import *


class AddressAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'street', 'town', 'postal_code', 'country')
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
    def __init__(self, *args, **kwargs):
        super(UserAdmin, self).__init__(*args, **kwargs)
        self.fieldsets += (('Extra', {'fields': ('gender', 'birth_date', 'home_address', 'mailing_address', 'school', 'graduation')}),)
        self.inlines = [UserPropertyInLine]
    list_display = ('username', 'first_name', 'last_name', 'email', 'school',
                    'get_is_staff', 'get_groups', 'is_active', 'get_properties')
    list_filter = ('groups', StaffFilter)
    search_fields = ('username', 'first_name', 'last_name')

    def get_groups(self, obj):
        return ", ".join([unicode(x) for x in obj.groups.all()])
    get_groups.short_description = 'skupiny'

    def get_is_staff(self, obj):
        return obj.is_staff
    get_is_staff.boolean = True
    get_is_staff.short_description = 'vedúci'

    def get_properties(self, obj):
        return unicode("<br>").join(unicode(x) for x in obj.properties.all())
    get_properties.short_description = 'dodatočné vlastnosti'
    get_properties.allow_tags = True



admin.site.register(Address, AddressAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(User, UserAdmin)
