from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from trojsten.login.backends import TrojstenOAuth2
from trojsten.login.serializers import UserSerializer
from trojsten.utils.utils import json_response

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse


@api_view(["GET"])
def get_current_user_info(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@json_response
def is_authenticated(request):
    return {"authenticated": request.user.is_authenticated}


@json_response
def userinfo(request):
    if not request.user.is_authenticated:
        return {"error": "Not logged in."}

    u = request.user
    return {
        "sub": str(u.id),
        "name": u.get_full_name(),
        "given_name": u.first_name,
        "family_name": u.last_name,
        "preferred_username": u.username,
        "email": u.email,
    }


def _autologin_urls():
    return (site.url for site in settings.SITES.values() if site.autologin)


def autologin_urls(request):
    url_suffix = reverse("social:begin", args=[TrojstenOAuth2.name])
    return JsonResponse(
        {"urls": list(urlparse.urljoin(url, url_suffix) for url in _autologin_urls())}
    )


def autologout_urls(request):
    url_suffix = reverse("account_logout")
    return JsonResponse(
        {"urls": list(urlparse.urljoin(url, url_suffix) for url in _autologin_urls())}
    )
