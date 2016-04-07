# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime
import pytz

from wiki.decorators import get_article

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.contrib import messages

from .models import Event, Invitation, EventType
from .forms import RegistrationForm


class ParticipantsAndOrganizersListView(DetailView):
    template_name = "trojsten/events/participants_and_organizers_list.html"
    model = Event
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'

participants_organizers_list = ParticipantsAndOrganizersListView.as_view()


class RegistrationView(FormView):
    template_name = "trojsten/events/registration.html"
    form_class = RegistrationForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RegistrationView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse(
            'event_registration',
            kwargs={'event_id': self.kwargs.get('event_id')},
        )

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        context['show_form'] = context['form'].invite.going is None
        context['after_deadline'] =\
            (
                False if context['form'].invite.event.registration_deadline is None else
                context['form'].invite.event.registration_deadline < datetime.now(pytz.utc)
            )
        return context

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(RegistrationView, self).get_form_kwargs()
        event = get_object_or_404(Event, pk=self.kwargs.get('event_id', None))
        if not event.registration:
            raise Http404
        try:
            kwargs['invite'] = Invitation.objects.select_related(
                'event__registration', 'user'
            ).get(user=self.request.user, event=event)
        except Invitation.DoesNotExist:
            raise PermissionDenied()
        return kwargs

    @method_decorator(transaction.atomic)
    def form_valid(self, form):
        if form.invite.going is not None:
            messages.add_message(
                self.request,
                messages.ERROR,
                'Prihláška nebola spracovaná, pretože bola vyplnená už predtým.',
            )
            return redirect(self.get_success_url())
        form.invite.going = form.cleaned_data['going']
        form.invite.save()
        if form.invite.going:
            for prop in form.invite.event.registration.required_user_properties.all():
                user_prop, _ = self.request.user.properties.get_or_create(
                    key=prop,
                )
                user_prop.value = form.cleaned_data[
                    RegistrationForm.PROPERTY_FIELD_NAME_TEMPLATE % prop.id
                ]
                user_prop.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Ďakujeme, prihláška bola spracovaná.',
        )
        return super(RegistrationView, self).form_valid(form)

registration = RegistrationView.as_view()


class EventView(DetailView):
    template_name = "trojsten/events/event.html"
    model = Event
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        context = super(EventView, self).get_context_data(**kwargs)
        context['invited'] = (
            self.request.user.is_authenticated()
            and context['event'].registration
            and Invitation.objects.select_related(
                'event__registration', 'user'
            ).filter(user=self.request.user, event=context['event']).exists()
        )
        return context

event_detail = EventView.as_view()


class EventListView(ListView):
    template_name = "trojsten/events/event_list.html"
    model = EventType
    context_object_name = 'event_types'
    queryset = EventType.objects.current_site_only().prefetch_related('event_set')

    # Hodnoty sa pridaju v dispatch()
    article = None
    urlpath = None

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
    queryset = EventType.objects.current_site_only().filter(
        is_camp=True
    ).prefetch_related('event_set')

camp_event_list = CampEventListView.as_view()
