from django.conf.urls import url

from .views import answer_query, task_view

app_name = "plugin_prask_2_4_1"

urlpatterns = [
    url(r"^api/query/?$", answer_query, name="answer_query"),
    url(r"^$", task_view, name="task_view"),
]
