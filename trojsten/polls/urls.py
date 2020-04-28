from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.view_question, name="view_question"),
    url(r"^anketa/(?P<pk>\d+)/$", views.view_question, name="view_question"),
]
