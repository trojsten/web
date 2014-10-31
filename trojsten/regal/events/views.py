from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404

from .models import Event
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

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(RegistrationView, self).get_form_kwargs()
        kwargs['event'] = get_object_or_404(Event, pk=self.kwargs.get('event_id'))
        return kwargs

