from django.conf.urls import patterns, url

urlpatterns = patterns('trojsten.task_statements.views',
    url(r'^notify_push/$', 'notify_push', name='notify_push'),
    url(r'^(?P<task_id>\d+)/$', 'task_statement', name='task_statement'),
)
