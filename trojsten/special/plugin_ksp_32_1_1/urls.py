from django.conf.urls import patterns, url

from trojsten.special.plugin_ksp_32_1_1 import views

urlpatterns = patterns(
    '',
    url(r'^$', views.main),
    url(r'^level/(?P<level>\d+)/', views.main, name="main"),
    url(r'^run/(?P<level>\d+)/', views.run, name="run"),
    url(r'^_update_all_points/', views.update_all_points, name="update_points"),
)
