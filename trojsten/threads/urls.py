from django.conf.urls import url

from .views import ThreadListView, ThreadView

urlpatterns = [
    url(r'^$', ThreadListView.as_view(), name='thread_list'),
    url(r'^(?P<thread_id>[0-9]+)/$', ThreadView.as_view(), name='thread'),
]
