from django.conf.urls import patterns, url
from django.contrib import admin

from .admin_views import merge_candidates, merge_users

urlpatterns = patterns('trojsten.regal.people.admin_views',
    url(r'^/merge/(?P<user_id>[0-9]+)$', admin.site.admin_view(merge_candidates), name='duplicate_user_candidate_list'),
    url(r'^/merge/(?P<user_id>[0-9]+)/(?P<candidate_id>[0-9]+)$', admin.site.admin_view(merge_users), name='duplicate_user_merge'),
)
