from django.conf.urls import include, url

urlpatterns = [
    url(
        r"^ksp/32/1/1/",
        include("trojsten.special.plugin_ksp_32_1_1.urls", namespace="plugin_ksp_32_1_1"),
    ),
    url(
        r"^ksp/32/2/1/",
        include("trojsten.special.plugin_ksp_32_2_1.urls", namespace="plugin_ksp_32_2_1"),
    ),
    url(r"^prask/1/2/1/", include("trojsten.special.plugin_prask_1_2_1.urls")),
    url(r"^prask/1/2/3/", include("trojsten.special.plugin_prask_1_2_3.urls")),
    url(r"^prask/2/1/3/", include("trojsten.special.plugin_prask_2_1_3.urls")),
    url(r"^prask/2/2/3/", include("trojsten.special.plugin_prask_2_2_3.urls")),
    url(r"^prask/2/3/3/", include("trojsten.special.plugin_prask_2_3_3.urls")),
    url(r"^prask/2/4/1/", include("trojsten.special.plugin_prask_2_4_1.urls")),
    url(r"^prask/2/4/3/", include("trojsten.special.plugin_prask_2_4_3.urls")),
    url(r"^prask/3/3/3/", include("trojsten.special.plugin_prask_3_3_3.urls")),
    url(
        r"^prask/5/1/1/",
        include("trojsten.special.plugin_prask_5_1_1.urls", namespace="plugin_prask_5_1_1"),
    ),
    url(
        r"^prask/5/1/2/",
        include("trojsten.special.plugin_prask_5_1_2.urls", namespace="plugin_prask_5_1_2"),
    ),
    url(
        r"^prask/7/1/1/",
        include("trojsten.special.plugin_prask_7_1_1.urls", namespace="plugin_prask_7_1_1"),
    ),
    url(
        r"^prask/7/2/1/",
        include("trojsten.special.plugin_prask_7_2_1.urls", namespace="plugin_prask_7_2_1"),
    ),
    url(
        r"^prask/8/1/1/",
        include("trojsten.special.plugin_prask_8_1_1.urls", namespace="plugin_prask_8_1_1"),
    ),
    url(
        r"^prask/8/2/4/",
        include("trojsten.special.plugin_prask_8_2_4.urls", namespace="plugin_prask_8_2_4"),
    ),
]
