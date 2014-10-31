from django.conf.urls import patterns, url


urlpatterns = patterns('trojsten.results.views',
    url(r'^(?P<event_id>(\d+))/zoznam_ucastnikov/$',
        'participants_organizers_list', name='participants_list'),
)
