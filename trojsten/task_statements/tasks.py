# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
from celery import shared_task
from trojsten.regal.contests.models import Repository
from django.conf import settings
from .git_api import pull_or_clone


def build(source_path, target_path):
    raise NotImplementedError


@shared_task
def compile_task_statements(repository_uuid):
    repository = Repository.objects.get(pk=repository_uuid)
    repo_url = repository.url
    repo_name = os.path.split(repo_url)[-1]
    repo_path = os.path.join(
        settings.TASK_STATEMENTS_REPO_PATH,
        repo_name,
    )
    pull_or_clone(repo_path, repo_url)
    build(repo_path, settings.TASK_STATEMENTS_PATH)
