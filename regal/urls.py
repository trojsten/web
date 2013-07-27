from django.conf.urls import patterns, include, url

urlpatterns = patterns('regal.views',
    url(r'^$','dashboard', name='dashboard'),
)
