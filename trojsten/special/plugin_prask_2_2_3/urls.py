from django.conf.urls import url

from .views import get_link

urlpatterns = [
    url(r'^$', get_link),
]
