from django.conf.urls import url
from trojsten.reviews.views import review_view
from django.contrib import admin

task_review_urls = [
    url(r'^(?P<task>[0-9]+)/review/$', admin.site.admin_view(review_view), name="task_review")
]