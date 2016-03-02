from django.conf.urls import patterns, url
from django.conf import settings


urlpatterns = patterns('trojsten.task_statements.views',
    url(r'^zadania/(?P<task_id>\d+)/$', 'task_statement', name='task_statement'),
    url(r'^riesenia/(?P<task_id>\d+)/$', 'solution_statement', name='solution_statement'),
    url(r'^(?P<round_id>\d+)/$', 'task_list', name='task_list'),
    url(r'^$', 'active_rounds_task_list', name='active_rounds_task_list'),
    url(r'^pdf/(?P<round_id>\d+)/', 'view_pdf', name='view_pdf'),
    url(r'^solutions_pdf/(?P<round_id>\d+)/', 'view_pdf',
        {'solution': True}, name='view_solutions_pdf'),
    url(r'^(?P<type>(zadania)|(riesenia))/(?P<task_id>\d+)/%s/(?P<picture>.+)$'
        % settings.TASK_STATEMENTS_PICTURES_DIR, 'show_picture', name='show_picture'),
    url(r'^ajax/(?P<round_id>\d+)/progressbar.html$', 'ajax_progressbar', name='ajax_progressbar'),
)
