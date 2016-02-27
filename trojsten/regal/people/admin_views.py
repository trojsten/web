# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render

from .helpers import get_similar_users
from .models import DuplicateUser, User


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


def merge_candidates(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    merge_candidates = get_similar_users(user)
    context = {
        'user': user,
        'merge_candidates': merge_candidates,
    }
    return render(
        request, 'admin/duplicate_user_candidate_list.html', context
    )


def merge_users(request, user_id, candidate_id):
    user = get_object_or_404(User, pk=user_id)
    candidate = get_object_or_404(User, pk=candidate_id)
    context = {
        'user': user,
        'candidate': candidate,
    }
    return render(
        request, 'admin/merge_duplicate_users.html', context
    )
