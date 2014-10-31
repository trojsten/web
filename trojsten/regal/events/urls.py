from django.conf.urls import patterns, url

from .views import RegistrationView

urlpatterns = patterns('trojsten.regal.events.views',
    url(r'^(?P<event_id>(\d+))/zoznam_ucastnikov/$',
        'participants_organizers_list', name='participants_list'),
    url(r'^(?P<event_id>(\d+))/prihlaska/$', RegistrationView.as_view(), name='participants_list'),
)
