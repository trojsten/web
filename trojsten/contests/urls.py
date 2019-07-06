from django.conf import settings
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^zadania/(?P<task_id>\d+)/$", views.task_statement, name="task_statement"),
    url(r"^riesenia/(?P<task_id>\d+)/$", views.solution_statement, name="solution_statement"),
    url(r"^(?P<round_id>\d+)/$", views.task_list, name="task_list"),
    url(r"^$", views.active_rounds_task_list, name="active_rounds_task_list"),
    url(r"^pdf/(?P<round_id>\d+)/", views.view_pdf, name="view_pdf"),
    url(
        r"^solutions_pdf/(?P<round_id>\d+)/",
        views.view_pdf,
        {"solution": True},
        name="view_solutions_pdf",
    ),
    url(
        r"^(?P<type>(zadania)|(riesenia))/(?P<task_id>\d+)/%s/(?P<picture>.+)$"
        % settings.TASK_STATEMENTS_PICTURES_DIR,
        views.show_picture,
        name="show_picture",
    ),
    url(
        r"^ajax/(?P<round_id>\d+)/progressbar.html$",
        views.ajax_progressbar,
        name="ajax_progressbar",
    ),
]
