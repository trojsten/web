from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('trojsten.submit.views',
    url(r'^(?P<task_id>\d+)/$', 'task_submit_form', name='task_submit_form'),
    url(r'^(?P<task_id>\d+)/list/$', 'task_submit_list', name='task_submit_list'),
    url(r'^(?P<task_id>\d+)/page/$', 'task_submit_page', name='task_submit_page'),
    url(r'^(?P<task_id>\d+)/(?P<submit_type>.+)/$', 'task_submit_post', name='task_submit_post'),
    url(r'^view/(?P<submit_id>\d+)/$', 'view_submit', name='view_submit'),
)
