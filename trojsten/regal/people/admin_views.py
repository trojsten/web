# -*- coding: utf-8 -*-
from django.shortcuts import render

from trojsten.regal.people.models import DuplicateUser, User


def duplicate_list(request):
    users = User.objects.filter(
        duplicateuser__status=DuplicateUser.MERGE_STATUS_UNRESOLVED,
    )
    context = {
        'users_to_merge': users,
    }
    return render(
        request, 'admin/view_duplicate_users.html', context
    )
