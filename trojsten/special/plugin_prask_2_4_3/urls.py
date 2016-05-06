from django.conf.urls import patterns, url

from .views import solved

urlpatterns = [
    url(r'^8WvjVD70u4ao/', solved, {'level': 1}),
    url(r'^ngsd7UqaNGUL/', solved, {'level': 2}),
    url(r'^0rzhyCSdubM4/', solved, {'level': 3}),
]
