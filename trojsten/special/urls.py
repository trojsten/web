from django.conf.urls import include, url


urlpatterns = [
    url(r'^ksp/32/1/1/', include('trojsten.special.plugin_ksp_32_1_1.urls',
        namespace='plugin_ksp_32_1_1', app_name='plugin_zwarte')),
    url(r'^ksp/32/2/1/', include('trojsten.special.plugin_ksp_32_2_1.urls',
        namespace='plugin_ksp_32_2_1', app_name='plugin_zwarte')),
    url(r'^ksp/32/3/1/', include('trojsten.special.plugin_ksp_32_3_1.urls')),
    url(r'^prask/1/2/1/', include('trojsten.special.plugin_prask_1_2_1.urls')),
    url(r'^prask/1/2/3/', include('trojsten.special.plugin_prask_1_2_3.urls')),
    url(r'^prask/2/1/3/', include('trojsten.special.plugin_prask_2_1_3.urls')),
    url(r'^prask/2/2/3/', include('trojsten.special.plugin_prask_2_2_3.urls')),
    url(r'^prask/2/3/3/', include('trojsten.special.plugin_prask_2_3_3.urls')),
    url(r'^prask/2/4/1/', include('trojsten.special.plugin_prask_2_4_1.urls')),
    url(r'^prask/2/4/3/', include('trojsten.special.plugin_prask_2_4_3.urls')),
]
