from django.conf.urls import url

from .views import main

urlpatterns = [url(r"^$", main, name="plugin_prask_1_2_3_main")]
