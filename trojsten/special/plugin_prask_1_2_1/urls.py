from django.conf.urls import patterns, url

from .views import *

urlpatterns =[
    url(r'^$', root,
        name='plugin_prask_1_2_1_root'),
    url(r'^(?P<category>[ABC])/$', main,
        name='plugin_prask_1_2_1_main'),
    url(r'^(?P<category>[ABC])/(?P<number>\d+)/$', main,
        name='plugin_prask_1_2_1_visit'),
    url(r'^(?P<category>[ABC])/post/$', post,
        name='plugin_prask_1_2_1_post'),
    url(r'^(?P<category>[ABC])/reset/$', reset,
        name='plugin_prask_1_2_1_reset'),
]
