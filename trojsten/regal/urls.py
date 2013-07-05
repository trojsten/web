from django.conf.urls import patterns, include, url

urlpatterns = patterns('trojsten.regal.views',
    # Examples:
    # url(r'^$', 'trojsten.views.home', name='home'),
    # url(r'^trojsten/', include('trojsten.foo.urls')),

    # table lists
    url(r'^addresses/(?P<filter>.*)/','show_addresses', name='addresses'),
    url(r'^persons/(?P<filter>\w*)/?','show_persons', name='persons'),
    url(r'^schools/(?P<filter>\w*)/?','show_schools', name='schools'),
    
    #default
    url(r'^$','show_home'),

    # test
    url(r'^print/(?P<word>\w+)/', 'print_word'),
    
)
