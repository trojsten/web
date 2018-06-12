# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from wiki.decorators import get_article

from .models import Event, EventType


class ParticipantsAndOrganizersListView(DetailView):
    template_name = "trojsten/events/participants_and_organizers_list.html"
    model = Event
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        context = super(ParticipantsAndOrganizersListView, self).get_context_data(**kwargs)
        event = context['event']
        participants = event.participants
        for participant in participants:
            participant.year_at_event = participant.user.school_year_at(event.start_time)
        context.update({
            'participants': participants,
            'organizers': event.organizers,
        })
        return context


participants_organizers_list = ParticipantsAndOrganizersListView.as_view()


class EventView(DetailView):
    template_name = "trojsten/events/event.html"
    model = Event
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'


event_detail = EventView.as_view()


class EventListView(ListView):
    template_name = "trojsten/events/event_list.html"
    model = EventType
    context_object_name = 'event_types'

    # Hodnoty sa pridaju v dispatch()
    article = None
    urlpath = None

    def get_queryset(self):
        return EventType.objects.current_site_only().prefetch_related('event_set')

    @method_decorator(get_article(can_read=True))
    def dispatch(self, request, article, *args, **kwargs):
        self.article = article
        self.urlpath = kwargs.get('urlpath', None)
        return super(EventListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context.update({
            'article': self.article,
            'urlpath': self.urlpath,
        })
        return context


event_list = EventListView.as_view()


class CampEventListView(EventListView):

    def get_queryset(self):
        return EventType.objects.current_site_only().filter(
            is_camp=True
        ).prefetch_related('event_set')


camp_event_list = CampEventListView.as_view()
