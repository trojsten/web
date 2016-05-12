from __future__ import absolute_import

from trojsten.login.views import login_root_view

from .common import *

urlpatterns += [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^$', login_root_view)
]
