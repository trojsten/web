from django.conf.urls import url
from django.views.generic.base import RedirectView

from trojsten.special.plugin_prask_7_1_1 import views
from .contants import LEVELS

app_name = "plugin_permonik"

urlpatterns = [
    url(r"^$", RedirectView.as_view(url='intro/', permanent=True)),
    url(r"^intro/$", views.intro),
    url(r"^get_hint/(?P<level>\d+)/", views.get_hint, name="get_hint"),
] + [url(fr"^{lvl.url}/$", views.level, {"level": id}) for (id, lvl) in enumerate(LEVELS)]