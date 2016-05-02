from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.event_list, {'path': '/akcie'}, name='event_list'),
    url(r'^sustredenia/$', views.camp_event_list, {'path': '/akcie/sustredenia', }, name='camp_event_list'),
    url(r'^(?P<event_id>(\d+))/$',
        views.event_detail, name='event_detail'),
    url(r'^(?P<event_id>(\d+))/zoznam_ucastnikov/$',
        views.participants_organizers_list, name='participants_list'),
    url(r'^(?P<event_id>(\d+))/prihlaska/$', views.registration,
        name='event_registration'),
]
