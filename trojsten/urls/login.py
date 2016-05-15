from __future__ import absolute_import

from trojsten.login.views import login_root_view
from trojsten.login.api import CurrentUserInfo

from .common import *

urlpatterns += [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^api/me/?$', CurrentUserInfo.as_view()),
    url(r'^$', login_root_view)
]
