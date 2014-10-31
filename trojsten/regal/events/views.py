from django.views.generic.base import TemplateView

from .models import Event


class ParticipantsAndOrganizersListView(TemplateView):
    template_name = "trojsten/regal/events/participants_and_organizers_list.html"

    def get_context_data(self, **kwargs):
        context = super(
            ParticipantsAndOrganizersListView, self
        ).get_context_data(**kwargs)

        event = Event.objects.get(
            pk=kwargs['event_id']
        )
        participants = event.participants.all()
        organizers = event.organizers.all()

        context.update({
            'event': event,
            'participants': participants,
            'organizers': organizers,
        })
        return context

participants_organizers_list = ParticipantsAndOrganizersListView.as_view()
