from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied


from .models import Event, Invitation
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

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(RegistrationView, self).get_form_kwargs()
        event = get_object_or_404(Event, pk=self.kwargs.get('event_id'))
        try:
            kwargs['invite'] = Invitation.objects.get(
                user=self.request.user, event=event
            )
        except Invitation.DoesNotExist:
            raise PermissionDenied()
        return kwargs

registration = RegistrationView.as_view()
