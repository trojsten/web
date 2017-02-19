from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.active_rounds_submit_page,
        name='active_rounds_submit_page'),
    url(r'^uloha/(?P<task_id>\d+)/$', views.task_submit_page,
        name='task_submit_page'),
    url(r'^kolo/(?P<round_id>\d+)/$', views.round_submit_page,
        name='round_submit_page'),
    url(r'^(?P<task_id>\d+)/(?P<submit_type>\d+)/$', views.task_submit_post,
        name='task_submit_post'),
    url(r'^ajax/old_submit/(?P<submit_id>\d+)/info.json$', views.poll_submit_info,
        name='poll_submit_info'),
    url(r'^ajax/old_submit/(?P<submit_id>\d+)/protokol/$', views.view_protocol,
        name='view_protocol'),
    url(r'^old_submit/(?P<submit_id>\d+)/$', views.view_submit, name='view_submit'),
    url(r'^protokol/(?P<protocol_id>\d+-\d+)/$', views.receive_protocol,
        name='receive_protocol'),
    url(r'^ajax/old_submit/(?P<submit_id>\d+)/komentar/$',
        views.view_reviewer_comment,
        name='view_reviewer_comment'),
    url(r'^ajax/externy_submit/$',
        views.external_submit,
        name='old_external_submit'),

]
