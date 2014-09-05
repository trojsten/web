from django.conf.urls import patterns, url


uuid_regex = '[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}'

urlpatterns = patterns('trojsten.task_statements.views',
    url(r'^notify_push/(?P<uuid>{uuid})/$'.format(uuid=uuid_regex), 'notify_push', name='notify_push'),
    url(r'^tasks/(?P<task_id>\d+)/$', 'task_statement', name='task_statement'),
    url(r'^solutions/(?P<task_id>\d+)/$', 'solution_statement', name='solution_statement'),
    url(r'^(?P<round_id>\d+)/$', 'task_list', name='task_list'),
    url(r'^$', 'latest_task_list', name='latest_task_list'),
    url(r'^pdf/(?P<round_id>\d+)/', 'view_pdf', name='view_pdf'),
)
