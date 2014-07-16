from __future__ import absolute_import

from celery import shared_task
from trojsten.regal.contests.models import Repository


@shared_task
def compile_task_statements(repository_uuid):
    repository = Repository.objects.get(pk=repository_uuid)
    return repository.url
