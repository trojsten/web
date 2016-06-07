from __future__ import absolute_import

import trojsten.login.views

from .common import *

urlpatterns += [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^ucet/logout', trojsten.login.views.logout),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^api/', include('trojsten.login.api_urls')),
    url(r'^$', trojsten.login.views.login_root_view)
]
