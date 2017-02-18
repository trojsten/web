from django.conf.urls import url
from django.contrib import admin

from .views import submitted_tasks


submitted_tasks_urls = [
    url(r'^(?P<user_pk>[0-9]+)/submitted_tasks/$',
        admin.site.admin_view(submitted_tasks), name='submitted_tasks')
]
