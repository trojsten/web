# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.encoding import force_text

from .models import *


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizers_group', 'get_sites')

    def get_sites(self, obj):
        return ', '.join(force_text(x) for x in obj.sites.all())
    get_sites.short_description = 'zobraziť na'


class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')


class ParticipantInvitationInline(admin.TabularInline):
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
    model = OrganizerInvitation
    fields = ('user', )
    extra = 1


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'place', 'start_time', 'end_time')
    inlines = [
        ParticipantInvitationInline, OrganizerInvitationInline
    ]


class InvitationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'type', 'going')


admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Place)
admin.site.register(Registration)
admin.site.register(Event, EventAdmin)
admin.site.register(Invitation, InvitationAdmin)
