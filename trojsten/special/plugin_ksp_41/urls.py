from django.conf.urls import url
from django.conf.urls import re_path
from django.views.static import serve
import re
import os

from trojsten.special.plugin_ksp_41 import views

app_name = "plugin_ksp_funkcie"

urlpatterns = [
    url(r"^$", views.main),
    url(r"^state$", views.state),
    url(r"^save$", views.save),
    url(r"^run$", views.run),
    re_path(r"^(?P<path>.*)$", serve, {"document_root": os.path.dirname(__file__) + "/static"},)
]
