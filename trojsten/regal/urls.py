from django.conf.urls import patterns, include, url

urlpatterns = patterns('trojsten.regal.views',
    # Examples:
    # url(r'^$', 'trojsten.views.home', name='home'),
    # url(r'^trojsten/', include('trojsten.foo.urls')),

    # test
    url(r'^(?P<word>\w+)/', 'print_word'),
)
