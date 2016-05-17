from __future__ import absolute_import

import trojsten.login.views
from trojsten.login.api import CurrentUserInfo, is_authenticated

from .common import *

urlpatterns += [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^ucet/logout', trojsten.login.views.logout),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^api/me/?$', CurrentUserInfo.as_view()),
    url(r'^api/checklogin/?$', is_authenticated),
    url(r'^$', trojsten.login.views.login_root_view)
]
