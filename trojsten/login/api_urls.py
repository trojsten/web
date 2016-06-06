from django.conf.urls import url

import trojsten.login.api

urlpatterns = [
    url(r'^me/?$', trojsten.login.api.CurrentUserInfo.as_view()),
    url(r'^checklogin/?$', trojsten.login.api.is_authenticated),
    url(r'^autologin_urls/?$', trojsten.login.api.autologin_urls),
    url(r'^autologout_urls/?$', trojsten.login.api.autologout_urls),
]
