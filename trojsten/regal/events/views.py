from django.views.generic.detail import DetailView

from .models import Event


class ParticipantsAndOrganizersListView(DetailView):
    template_name = "trojsten/regal/events/participants_and_organizers_list.html"
    model = Event
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'

participants_organizers_list = ParticipantsAndOrganizersListView.as_view()
