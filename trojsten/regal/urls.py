from django.conf.urls import patterns, include, url

urlpatterns = patterns('trojsten.regal.views',
    # Examples:
    # url(r'^$', 'trojsten.views.home', name='home'),
    # url(r'^trojsten/', include('trojsten.foo.urls')),

    # table lists
    url(r'^address/(?P<filter>.*)/?','show_address'),
    #url(r'^person/(?P<filter>\w*)/?','show_person'),
    #url(r'^school/(?P<filter>\w*)/?','show_school'),

    # test
    url(r'^print/(?P<word>\w+)/', 'print_word'),
)
