from django.conf.urls import url

from trojsten.login import api

urlpatterns = [
    url(r"^me/?$", api.get_current_user_info),
    url(r"^checklogin/?$", api.is_authenticated),
    url(r"^autologin_urls/?$", api.autologin_urls),
    url(r"^autologout_urls/?$", api.autologout_urls),
]
