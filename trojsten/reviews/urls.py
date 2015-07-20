from django.conf.urls import url
from trojsten.reviews.views import (review_task, submit_download,
                                    download_latest_submits, zip_upload)
from django.contrib import admin

task_review_urls = [
    url(r'^(?P<task_pk>[0-9]+)/download_latest_submits$',
        admin.site.admin_view(download_latest_submits), name='download_latest_submits'),
    url(r'^(?P<task_pk>[0-9]+)/review/$',
        admin.site.admin_view(review_task), name='review_task'),
    url(r'^(?P<task_pk>[0-9]+)/review/zip_upload/$',
        admin.site.admin_view(zip_upload), name='review_submit_zip'),
]

submit_urls = [
    url(r'^(?P<submit_pk>[0-9]+)/download/$',
        admin.site.admin_view(submit_download), name='submit_download'),
]
