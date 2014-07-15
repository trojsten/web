from __future__ import absolute_import

from celery import shared_task


@shared_task
def compile_task_statements():
    return 47
