from django.conf.urls import patterns, url

urlpatterns = patterns('trojsten.regal.people.admin_views',
    url(r'^/manage$', 'duplicate_list', name='duplicate_user_list'),
    url(r'^/merge/(?P<user_id>[0-9]+)$', 'merge_candidates', name='duplicate_user_candidate_list'),
    url(r'^/merge/(?P<user_id>[0-9]+)/(?P<candidate_id>[0-9]+)$', 'merge_users', name='duplicate_user_merge'),
)
