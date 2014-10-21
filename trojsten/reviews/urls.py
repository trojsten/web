from django.conf.urls import url
from trojsten.reviews.views import task_view, task_user_view, submit_download_view, download_latest_submits_view
from django.contrib import admin

task_review_urls = [
    url(r'^(?P<task_pk>[0-9]+)/download_latest_submits$', admin.site.admin_view(download_latest_submits_view), name="download_latest_submits"),
    url(r'^(?P<task_pk>[0-9]+)/review/$', admin.site.admin_view(task_view), name="review_task"),
    url(r'^(?P<task_pk>[0-9]+)/review/(?P<user_pk>(all|[0-9]+))$', admin.site.admin_view(task_user_view), name="review_task_user"),
]

submit_urls = [
	url(r'^(?P<submit_pk>[0-9]+)/download/$', admin.site.admin_view(submit_download_view), name="submit_download"),
]