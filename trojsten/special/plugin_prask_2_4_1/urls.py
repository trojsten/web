from django.conf.urls import patterns, url
from .views import task_view, answer_query, submit

app_name = 'plugin_prask_2_4_1'

urlpatterns = patterns(
    url(r'^api/query/?$', answer_query, name='plugin_prask_2_4_1:answer_query'),
    url(r'^api/submit/?$', submit, name='plugin_prask_2_4_1:submit'),
    url(r'^$', task_view, name='plugin_prask_2_4_1:task_view'),
)
