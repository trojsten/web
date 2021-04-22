from django.conf.urls import url
from django.views.generic.base import RedirectView, TemplateView

from trojsten.special.plugin_prask_7_2_1 import views

from .constants import LEVELS

app_name = "plugin_permonik2"

urlpatterns = [
    url(r"^$", RedirectView.as_view(url="intro/", permanent=True)),
    url(r"^intro/$", views.intro),
    url(r"^get_hint/(?P<level>\d+)/$", views.get_hint, name="get_hint"),
    url(
        r"^get_params_text/$",
        TemplateView.as_view(template_name="plugin_prask_7_2_1/get_params.html"),
        name="get_params",
    ),
    url(
        r"^(frozen|ladovekralovstvo|ladove_kralovstvo)/$",
        TemplateView.as_view(template_name="plugin_prask_7_2_1/frozen.html"),
    ),
] + [
    url(r"^%s/$" % lvl.url, views.level, {"level": id, "source_fname": lvl.source_fname})
    for (id, lvl) in enumerate(LEVELS)
]
