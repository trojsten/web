from django.conf.urls import patterns, url

urlpatterns = patterns('trojsten.regal.events.views',
    url(r'^$', 'event_list', {'path': '/akcie'}, name='event_list'),
    url(r'^sustredenia/$', 'camp_event_list', {'path': '/akcie/sustredenia', }, name='camp_event_list'),
    url(r'^(?P<event_id>(\d+))/$',
        'event_detail', name='event_detail'),
    url(r'^(?P<event_id>(\d+))/zoznam_ucastnikov/$',
        'participants_organizers_list', name='participants_list'),
    url(r'^(?P<event_id>(\d+))/prihlaska/$', 'registration',
        name='event_registration'),
)
