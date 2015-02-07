# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
    template_name = "trojsten/regal/events/participants_and_organizers_list.html"
    model = Event
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'

participants_organizers_list = ParticipantsAndOrganizersListView.as_view()


class RegistrationView(FormView):
    template_name = "trojsten/regal/events/registration.html"
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
    template_name = "trojsten/regal/events/event.html"
    model = Event
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'

event_detail = EventView.as_view()


class EventListView(ListView):
    template_name = "trojsten/regal/events/event_list.html"
    model = EventType
    context_object_name = 'event_types'
    query_set = EventType.objects.current_site_only()

event_list = EventListView.as_view()
