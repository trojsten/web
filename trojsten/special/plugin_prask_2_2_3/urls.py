from django.conf.urls import patterns, url

from .views import get_link

urlpatterns = patterns(
    '',
    url(r'^$', get_link),
)
