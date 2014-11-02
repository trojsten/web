# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django import forms
from django.utils.encoding import force_text

from .models import *


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizers_group', 'get_sites')

    def get_sites(self, obj):
        return ', '.join(force_text(x) for x in obj.sites.all())
    get_sites.short_description = 'zobraziť na'


class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')


class ParticipantModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ParticipantModelForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = [
            choice for choice in self.fields['type'].choices
            if choice[0] != Invitation.ORGANIZER
        ]


class ParticipantInvitationInline(admin.StackedInline):
    model = Invitation
    form = ParticipantModelForm
    extra = 1
    fields = (('user', 'type'),)
    verbose_name = 'účastník'
    verbose_name_plural = 'účastníci'

    def get_queryset(self, request):
        qs = super(ParticipantInvitationInline, self).get_queryset(request)
        return qs.exclude(type=Invitation.ORGANIZER)


class OrganizerModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizerModelForm, self).__init__(*args, **kwargs)
        self.fields['type'].initial = Invitation.ORGANIZER
        self.fields['type'].widget = forms.widgets.HiddenInput()
        self.fields['type'].label = ''
        self.fields['user'].label = 'Vedúci:'


class OrganizerInvitationInline(admin.StackedInline):
    form = OrganizerModelForm
    model = Invitation
    extra = 1
    fields = (('user', 'type'),)
    verbose_name = 'vedúci'

    def get_queryset(self, request):
        qs = super(OrganizerInvitationInline, self).get_queryset(request)
        return qs.filter(type=Invitation.ORGANIZER)


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
admin.site.register(Event, EventAdmin)
admin.site.register(Invitation, InvitationAdmin)
