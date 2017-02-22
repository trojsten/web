from django.conf.urls import url

from trojsten.submit_utils import views

urlpatterns = [
    url(r'^$', views.active_rounds_submit_page,
        name='active_rounds_submit_page'),
    url(r'^uloha/(?P<task_id>\d+)/$', views.task_submit_page,
        name='task_submit_page'),
    url(r'^kolo/(?P<round_id>\d+)/$', views.round_submit_page,
        name='round_submit_page'),
]
