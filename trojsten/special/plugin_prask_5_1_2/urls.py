from django.conf.urls import url

from trojsten.special.plugin_prask_5_1_2 import views

app_name = 'plugin_zwarte'

urlpatterns = [
    url(r'^$', views.main),
    url(r'^level/(?P<level>\d+)/', views.main, name="main"),
    url(r'^run/(?P<level>\d+)/', views.run, name="run"),
]
