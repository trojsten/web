from django.conf.urls import patterns, url

uuid_regex = '[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}'

urlpatterns = patterns('trojsten.task_statements.views',
    url(r'^notify_push/(?P<uuid>{uuid})/$'.format(uuid=uuid_regex), 'notify_push', name='notify_push'),
    url(r'^(?P<task_id>\d+)/$', 'task_statement', name='task_statement'),
    url(r'^solutions/(?P<task_id>\d+)/$', 'solution_statement', name='solution_statement'),
)
