# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.encoding import force_text

from .models import *


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizers_group', 'get_sites')

    def get_sites(self, obj):
        return ', '.join(force_text(x) for x in obj.sites.all())
    get_sites.short_description = 'doména akcie'


class EventLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'place', 'start_time', 'end_time')


class EventIvitationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'type', 'going')


admin.site.register(EventType, EventTypeAdmin)
admin.site.register(EventLink, EventLinkAdmin)
admin.site.register(EventPlace)
admin.site.register(Event, EventAdmin)
admin.site.register(EventInvitation, EventIvitationAdmin)
