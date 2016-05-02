from __future__ import absolute_import

from .common import *

urlpatterns += [
    url(r'', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^ucet/', include('ksp_login.urls')),
]
