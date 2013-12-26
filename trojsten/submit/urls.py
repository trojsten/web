from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('trojsten.submit.views',
                       url(r'^(?P<task_id>\d+)/$',
                           'task_submit_form', name='task_submit_form'),
                       url(r'^(?P<task_id>\d+)/(?P<submit_type>.+)/$',
                           'task_submit_post', name='task_submit_post'),
                       )
