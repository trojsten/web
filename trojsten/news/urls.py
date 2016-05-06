from django.conf.urls import include, patterns, url

from trojsten.news.feeds import NewsFeed
from trojsten.news.views import EntryListView

urlpatterns = [
    url(r'^strana/(?P<page>[0-9]+)/$', EntryListView.as_view(),
        name='news_list'),
    url(r'^feed/$', NewsFeed(), name='news_feed'),
]
