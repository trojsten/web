from django.urls import path

from trojsten.special.plugin_prask_8_1_1 import views

app_name = "plugin_zergbot"

urlpatterns = [
    path("", views.index, name="root"),
    path("levels/", views.levels),
    path("levels/s<int:sid>l<int:lid>/", views.level),
    path("solutions/s<int:sid>l<int:lid>/", views.solution),
]
