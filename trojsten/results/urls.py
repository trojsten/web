from django.conf.urls import patterns, url

urlpatterns = patterns('trojsten.results.views',
    url(r'^(?P<round_id>(\d+))/$', 'view_results', name='view_results'),
    url(r'^(?P<round_id>(\d+))/(?P<category_id>(\d+))/$', 'view_results', name='view_results'),
    url(r'^$', 'view_latest_results', name='view_latest_results'),
)
