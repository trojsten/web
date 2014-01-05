from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('trojsten.submit.views',
    url(r'^(?P<task_id>\d+)/$', 'task_submit_page', name='task_submit_page'),
    url(r'^(?P<task_id>\d+)/(?P<submit_type>.+)/$', 'task_submit_post', name='task_submit_post'),
    url(r'^view/(?P<submit_id>\d+)/$', 'view_submit', name='view_submit'),
)
