# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from easy_select2 import select2_modelform
from easy_select2.widgets import Select2
from import_export import fields, resources
from import_export.admin import ExportMixin
from trojsten.regal.contests.models import Competition, Series
from trojsten.regal.people.models import (Address, DuplicateUser, School, User,
                                          UserProperty, UserPropertyKey)
from trojsten.regal.tasks.models import Submit
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


class ActiveInCompetitionFilter(admin.SimpleListFilter):
    title = 'účasti v súťaži'
    parameter_name = 'competition'

    def lookups(self, request, model_admin):
        return ((c.id, force_text(c)) for c in Competition.objects.all())

    def queryset(self, request, queryset):
        if self.value():
            active_users = Submit.objects.filter(
                task__round__series__competition__id=self.value()
            ).values_list('user', flat=True)
            return queryset.filter(id__in=active_users)
        else:
            return queryset


class ActiveInSeriesSubFilter(admin.SimpleListFilter):
    title = 'účasti v sérii'
    parameter_name = 'series'

    def lookups(self, request, model_admin):
        series = Series.objects
        if 'competition' in request.GET:
            series = series.filter(competition__id=request.GET['competition'])
        return ((s.id, force_text(s)) for s in series.all())

    def queryset(self, request, queryset):
        if self.value():
            active_users = Submit.objects.filter(
                task__round__series__id=self.value()
            ).values_list('user', flat=True)
            return queryset.filter(id__in=active_users)
        else:
            return queryset


class UsersExport(resources.ModelResource):
    street = fields.Field()
    town = fields.Field()
    postal_code = fields.Field()
    country = fields.Field()

    class Meta:
        model = User
        export_order = fields = (
            'first_name', 'last_name', 'birth_date', 'email', 'graduation',
            'street', 'town', 'postal_code', 'country',
            'school__verbose_name', 'school__addr_name', 'school__street',
            'school__city', 'school__zip_code'
        )
        widgets = {'birth_date': {'format': '%d.%m.%Y'}}

    def dehydrate_street(self, obj):
        address = obj.get_mailing_address()
        return '' if address is None else address.street

    def dehydrate_town(self, obj):
        address = obj.get_mailing_address()
        return '' if address is None else address.town

    def dehydrate_postal_code(self, obj):
        address = obj.get_mailing_address()
        return '' if address is None else address.postal_code

    def dehydrate_country(self, obj):
        address = obj.get_mailing_address()
        return '' if address is None else address.country


class UserAdmin(ExportMixin, DefaultUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'get_school', 'graduation', 'get_is_staff', 'get_groups',
                    'is_active', 'get_properties')
    list_filter = ('groups', StaffFilter, ActiveInCompetitionFilter, ActiveInSeriesSubFilter)
    search_fields = ('username', 'first_name', 'last_name')

    formfield_overrides = {
        models.ForeignKey: {'widget': Select2()}
    }

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'email', 'gender', 'birth_date'
        )}),
        (_('Address'), {'fields': ('home_address', 'mailing_address')}),
        (_('School'), {'fields': ('school', 'graduation')}),
    )
    superuser_fieldsets = fieldsets + (
        (_('Permissions'), {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        )}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    inlines = (UserPropertyInLine,)

    resource_class = UsersExport

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        return qs.select_related('school').prefetch_related(
            'groups', 'properties__key'
        )

    def get_fieldsets(self, request, obj=None):
        if obj is None or not request.user.is_superuser:
            return super(UserAdmin, self).get_fieldsets(request, obj)
        else:
            return self.superuser_fieldsets

    def get_groups(self, obj):
        return ', '.join(force_text(x) for x in obj.groups.all())
    get_groups.short_description = 'skupiny'

    get_is_staff = attribute_format(attribute='is_staff', description='vedúci', boolean=True)

    def get_school(self, obj):
        if obj.school.has_abbreviation:
            show = obj.school.abbreviation
        else:
            show = obj.school.verbose_name
        return '<span title="%s">%s</span>' % (
            escape(force_text(obj.school)), escape(force_text(show))
        )
    get_school.short_description = 'škola'
    get_school.admin_order_field = 'school'
    get_school.allow_tags = True

    def get_properties(self, obj):
        return '<br />'.join(escape(force_text(x)) for x in obj.properties.all())
    get_properties.short_description = 'dodatočné vlastnosti'
    get_properties.allow_tags = True


class DuplicateUserAdmin(admin.ModelAdmin):
    form = select2_modelform(DuplicateUser)
    list_display = ('user', 'status', 'actions_field')
    ordering = ('status', 'user')
    list_filter = ('status',)

    def actions_field(self, obj):
        return '<a href="%s">%s</a>' % (
            reverse(
                'duplicate_user_candidate_list',
                kwargs={'user_id': '%s' % obj.user.id}
            ),
            _('Candidate list'),
        )
    actions_field.allow_tags = True
    actions_field.short_description = _('Actions')


admin.site.register(Address, AddressAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(DuplicateUser, DuplicateUserAdmin)
admin.site.register(UserPropertyKey)
