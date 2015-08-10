from django.conf.urls import patterns, url

from .views import ThreadView, ThreadListView

urlpatterns = patterns('',
    url(r'^$', ThreadListView.as_view(), name='thread_list'),
    url(r'^(?P<thread_id>[0-9]+)/$', ThreadView.as_view(), name='thread'),
)