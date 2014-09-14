from django.conf.urls import patterns, include, url

from trojsten.news.views import EntryListView
from trojsten.news.feeds import NewsFeed


urlpatterns = patterns('',
    url(r'^strana/(?P<page>[0-9]+)/$', EntryListView.as_view(),
        name='news_list'),
    url(r'^feed/$', NewsFeed(), name='news_feed'),
)
