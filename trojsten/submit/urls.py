from django.conf.urls import patterns, url

urlpatterns = patterns('trojsten.submit.views',
    url(r'^uloha/(?P<task_id>\d+)/$', 'task_submit_page', name='task_submit_page'),
    url(r'^kolo/(?P<round_id>\d+)/$', 'round_submit_page', name='round_submit_page'),
    url(r'^(?P<task_id>\d+)/(?P<submit_type>\d+)/$', 'task_submit_post', name='task_submit_post'),
    url(r'^submit/(?P<submit_id>\d+)/$', 'view_submit', name='view_submit'),
    url(r'^protokol/(?P<protocol_id>\d+-\d+)/$', 'receive_protocol', name='receive_protocol'),
)
