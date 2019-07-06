# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

try:
    from urllib2 import quote
except ImportError:
    from urllib.parse import quote


@login_required
def login_root_view(request):
    return render(request, "trojsten/login/base.html")


def logout(request):
    next_url = request.GET.get("next_page", "/")
    response = LogoutView.as_view(next_page=next_url)(request)
    messages.success(request, _("Logout successful"))
    if urlparse.urlparse(next_url).netloc:
        return redirect(next_url)
    return response


def remote_logout(request):
    logout_url = urlparse.urljoin(settings.TROJSTEN_LOGIN_PROVIDER_URL, reverse("account_logout"))
    next_url = request.GET.get("next_page", "/")
    request.GET = request.GET.copy()
    LogoutView.as_view()(request)
    return redirect("%s?next_page=%s" % (logout_url, quote(request.build_absolute_uri(next_url))))
