from __future__ import absolute_import

from .common import *
from trojsten.views import login_root_view

urlpatterns += [
    url(r'oauth', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'', login_root_view)
]
