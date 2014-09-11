from django.conf.urls import patterns, url

urlpatterns = patterns('trojsten.results.views',
    url(r'^(?P<round_ids>(\d+(,\d+)*))/$', 'view_results', name='view_results'),
    url(r'^(?P<round_ids>(\d+(,\d+)*))/(?P<category_ids>(\d+(,\d+)*))/$', 'view_results', name='view_results'),
)
