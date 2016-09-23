# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_text
from easy_select2 import select2_modelform
from import_export import fields, resources
from import_export.admin import ExportMixin

from .models import Event, EventType, Invitation, OrganizerInvitation, Link, Place, Registration


class EventTypeAdmin(admin.ModelAdmin):
    form = select2_modelform(EventType)
    list_display = ('name', 'organizers_group', 'get_sites', 'is_camp')

    def get_sites(self, obj):
        return ', '.join(force_text(x) for x in obj.sites.all())
    get_sites.short_description = 'zobraziť na'


class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')


class ParticipantInvitationInline(admin.TabularInline):
    form = select2_modelform(Invitation)
    model = Invitation
    extra = 1
    fields = ('user', 'type'),
    verbose_name = 'účastník'
    verbose_name_plural = 'účastníci'

    def get_queryset(self, request):
        qs = super(ParticipantInvitationInline, self).get_queryset(request)
        return qs.exclude(type=Invitation.ORGANIZER)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'type':
            kwargs['choices'] = [
                choice for choice in db_field.get_choices(include_blank=False)
                if choice[0] != Invitation.ORGANIZER
            ]
        return super(
            ParticipantInvitationInline, self
        ).formfield_for_choice_field(db_field, request, **kwargs)


class OrganizerInvitationInline(admin.TabularInline):
    form = select2_modelform(Invitation)
    model = OrganizerInvitation
    fields = ('user', )
    extra = 1


class EventAdmin(admin.ModelAdmin):
    form = select2_modelform(Event)
    list_display = ('name', 'type', 'place', 'start_time', 'end_time', 'registration_deadline')
    inlines = [
        ParticipantInvitationInline, OrganizerInvitationInline
    ]

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        events_type_lst = EventType.objects.filter(organizers_group__in=user_groups)
        return super(EventAdmin, self).get_queryset(request).filter(
            type__in=events_type_lst
        )


class InvitedUsersExport(resources.ModelResource):
    type = fields.Field()

    street = fields.Field()
    town = fields.Field()
    postal_code = fields.Field()
    country = fields.Field()

    class Meta:
        model = Invitation
        export_order = fields = [
            'user__first_name', 'user__last_name', 'user__birth_date', 'user__email',
            'street', 'town', 'postal_code', 'country',
            'user__school__verbose_name', 'type', 'going'
        ]
        widgets = {'user__birth_date': {'format': '%d.%m.%Y'}}

    def dehydrate_type(self, obj):
        return obj.get_type_display()

    def dehydrate_street(self, obj):
        address = obj.user.get_mailing_address()
        return '' if address is None else address.street

    def dehydrate_town(self, obj):
        address = obj.user.get_mailing_address()
        return '' if address is None else address.town

    def dehydrate_postal_code(self, obj):
        address = obj.user.get_mailing_address()
        return '' if address is None else address.postal_code

    def dehydrate_country(self, obj):
        address = obj.user.get_mailing_address()
        return '' if address is None else address.country

    def export(self, queryset=None):
        """
        Overrides export to add columns with additional user properties
        required in event registration form.
        """
        def create_access_method(prop_key):
            def returned_method(obj):
                try:
                    return obj.user.properties.get(key=prop_key).value
                except ObjectDoesNotExist:
                    return ''
            return returned_method

        if queryset and not (queryset.first().event.registration is None):
            property_keys = queryset.first().event.registration.required_user_properties.all()
            for property_key in property_keys:
                access_method_name = 'property_%i' % property_key.id
                self._meta.export_order.append(access_method_name)
                self.fields[access_method_name] = fields.Field(column_name=property_key.key_name)
                setattr(self, 'dehydrate_%s' % access_method_name, create_access_method(property_key))

        return super(InvitedUsersExport, self).export(queryset)


class InvitationAdmin(ExportMixin, admin.ModelAdmin):
    form = select2_modelform(Invitation)
    list_display = ('event', 'user', 'type', 'going')
    resource_class = InvitedUsersExport
    list_filter = ('event', 'going')

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        events_type_lst = EventType.objects.filter(organizers_group__in=user_groups)
        events_lst = Event.objects.filter(type__in=events_type_lst)
        return super(InvitationAdmin, self).get_queryset(request).filter(
            event__in=events_lst
        )


admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Place)
admin.site.register(Registration)
admin.site.register(Event, EventAdmin)
admin.site.register(Invitation, InvitationAdmin)
