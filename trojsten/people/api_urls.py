from django.conf.urls import url

from trojsten.people import api

urlpatterns = [
    url(r'^switch_contest_participation/?$', api.switch_contest_participation, name='switch_contest_participation'),
]
