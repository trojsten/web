from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^(?P<round_id>(\d+))/$", views.view_results, name="view_results"),
    url(r"^(?P<round_id>(\d+))/(?P<tag_key>(.+))/$", views.view_results, name="view_results"),
    url(r"^$", views.view_latest_results, name="view_latest_results"),
    url(r"^susiXP/(?P<round_id>(\d+))/$", views.explain_susi_xp, name="explain_susi_xp"),
]
