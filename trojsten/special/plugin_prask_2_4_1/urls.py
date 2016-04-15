from django.conf.urls import patterns, url
from .views import task_view, answer_query

app_name = 'plugin_prask_2_4_1'

urlpatterns = patterns(
    url(r'^api/query/?$', answer_query, name='answer_query'),
    url(r'^$', task_view, name='task_view'),
)
