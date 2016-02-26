from django.conf.urls import patterns, url

urlpatterns = patterns('trojsten.regal.people.admin_views',
    url(r'^/manage$', 'duplicate_list', name='duplicate_user_list'),
)
