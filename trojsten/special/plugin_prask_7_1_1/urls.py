from django.conf.urls import url
from django.views.generic.base import RedirectView

from trojsten.special.plugin_prask_7_1_1 import views

from .constants import LEVELS

app_name = "plugin_permonik"

urlpatterns = [
    url(r"^$", RedirectView.as_view(url="intro/", permanent=True)),
    url(r"^intro/$", views.intro),
    url(r"^get_hint/(?P<level>\d+)/$", views.get_hint, name="get_hint"),
    url(r"^get_button_password/$", views.get_button_password, name="get_button_password"),
    url(r"^get_input_password/$", views.get_input_password, name="get_input_password"),
] + [
    url(r"^%s/$" % lvl.url, views.level, {"level": id, "source_fname": lvl.source_fname})
    for (id, lvl) in enumerate(LEVELS)
]
