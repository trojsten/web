# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _

from . import constants
from .forms import MergeForm
from .helpers import get_similar_users, merge_users
from .models import User


def merge_candidates_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    merge_candidates = get_similar_users(user)
    context = {
        'user': user,
        'merge_candidates': merge_candidates,
    }
    return render(
        request, 'admin/duplicate_user_candidate_list.html', context
    )


def merge_users_view(request, user_id, candidate_id):
    user = get_object_or_404(User, pk=user_id)
    candidate = get_object_or_404(User, pk=candidate_id)
    if request.method == 'POST':
        form = MergeForm(user, candidate, request.POST)
        if form.is_valid():
            target_user, source_user = (user, candidate) if form.cleaned_data['id'] == user.id else\
                (candidate, user)

            src_fields = [
                key for key, val in filter(
                    lambda (k, _): k != 'id' and not k.startswith(constants.USER_PROP_PREFIX),
                    form.cleaned_data.items()
                ) if int(val) == source_user.pk
            ]
            src_user_props = [
                int(key[len(constants.USER_PROP_PREFIX):]) for key, val in filter(
                    lambda (k, _): k.startswith(constants.USER_PROP_PREFIX),
                    form.cleaned_data.items()
                ) if int(val) == source_user.pk
            ]

            merge_users(target_user, source_user, src_fields, src_user_props)
            messages.add_message(request, messages.SUCCESS, _('Users merged succesfully.'))
            return redirect('duplicate_user_candidate_list', user_id=target_user.pk)
        else:
            print form.cleaned_data
            messages.add_message(request, messages.ERROR, _('Error when merging users.'))
    else:
        form = MergeForm(user, candidate)
    context = {
        'user': user,
        'candidate': candidate,
        'form': form,
    }
    return render(
        request, 'admin/merge_duplicate_users.html', context
    )
