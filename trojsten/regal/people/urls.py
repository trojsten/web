from django.conf.urls import patterns, url
from django.contrib import admin

from .admin_views import merge_candidates_view, merge_users_view

urlpatterns = patterns('trojsten.regal.people.admin_views',
    url(r'^/merge/(?P<user_id>[0-9]+)$', admin.site.admin_view(merge_candidates_view), name='duplicate_user_candidate_list'),
    url(r'^/merge/(?P<user_id>[0-9]+)/(?P<candidate_id>[0-9]+)$', admin.site.admin_view(merge_users_view), name='duplicate_user_merge'),
)
