from django.conf.urls import patterns, url

from .views import get_link

urlpatterns = [
    url(r'^$', get_link),
]
