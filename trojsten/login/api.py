try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from oauth2_provider.views.generic import ProtectedResourceView


class CurrentUserInfo(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        user = request.user
        user_info = {
            'uid': user.username,
        }
        return JsonResponse(user_info)


def is_authenticated(request):
    return JsonResponse({'authenticated': request.user.is_authenticated()})


def _autologin_urls():
    return (site.url for site in settings.SITES.values() if site.autologin)


def autologin_urls(request):
    url_suffix = reverse('account_login')
    return JsonResponse({ 'urls': list(urlparse.urljoin(url, url_suffix) for url in _autologin_urls())})


def autologout_urls(request):
    url_suffix = reverse('account_logout')
    return JsonResponse({'urls': list(urlparse.urljoin(url, url_suffix) for url in _autologin_urls())})
