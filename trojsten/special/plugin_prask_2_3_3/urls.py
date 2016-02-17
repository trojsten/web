from django.conf.urls import patterns, url

from .views import solved

urlpatterns = patterns(
    '',
    url(r'^yhgtdyuox/', solved, {'level': 1}),
    url(r'^wbqqdyhgtd/', solved, {'level': 2}),
    url(r'^syuyzgomo/', solved, {'level': 3}),
)
