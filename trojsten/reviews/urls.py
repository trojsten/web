from django.conf.urls import url
from django.contrib import admin

from trojsten.reviews.views import (
    download_latest_reviewed_submits,
    download_latest_submits,
    edit_review,
    review_task,
    submit_download,
    zip_upload,
)

task_review_urls = [
    url(
        r"^(?P<task_pk>[0-9]+)/download_latest_submits$",
        admin.site.admin_view(download_latest_submits),
        name="download_latest_submits",
    ),
    url(
        r"^(?P<task_pk>[0-9]+)/download_latest_reviewed_submits$",
        admin.site.admin_view(download_latest_reviewed_submits),
        name="download_latest_reviewed_submits",
    ),
    url(r"^(?P<task_pk>[0-9]+)/review/$", admin.site.admin_view(review_task), name="review_task"),
    url(
        r"^(?P<task_pk>[0-9]+)/review/zip_upload/$",
        admin.site.admin_view(zip_upload),
        name="review_submit_zip",
    ),
    url(
        r"^(?P<task_pk>[0-9]+)/review/edit/(?P<submit_pk>[0-9]+)/",
        admin.site.admin_view(edit_review),
        name="review_edit",
    ),
]

submit_urls = [
    url(
        r"^(?P<submit_pk>[0-9]+)/download/$",
        admin.site.admin_view(submit_download),
        name="submit_download",
    )
]
