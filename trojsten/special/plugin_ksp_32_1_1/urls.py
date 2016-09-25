from django.conf.urls import url

from trojsten.special.plugin_ksp_32_1_1 import views

urlpatterns = [
    url(r'^$', views.main),
    url(r'^level/(?P<level>\d+)/', views.main, name="main"),
    url(r'^run/(?P<level>\d+)/', views.run, name="run"),
]
