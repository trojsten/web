from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^ksp/32/1/1/', include('trojsten.special.plugin_ksp_32_1_1.urls')),
    url(r'^ksp/32/2/1/', include('trojsten.special.plugin_ksp_32_2_1.urls')),
)
