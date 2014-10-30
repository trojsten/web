from django.conf.urls import patterns, url

from .views import ParticipantsAndOrganizersListView

urlpatterns = patterns('trojsten.results.views',
    url(r'^(?P<event_id>(\d+))/zoznam_ucastnikov/$', ParticipantsAndOrganizersListView.as_view(), name='participants_list'),
)
