# -*- coding: utf-8 -*-
from __future__ import absolute_import

import rules
from django.core.exceptions import ObjectDoesNotExist
from rules.contrib.admin import \
    ObjectPermissionsModelAdmin as RulesObjectPermissionsModelAdmin


def get_predicate_from_filter(db_query):
    @rules.predicate
    def db_filter_predicate(user, obj):
        if obj is None:
            return None
        try:
            obj.__class__.objects.filter(db_query(user)).get(pk=obj.pk)
            return True
        except ObjectDoesNotExist:
            return False
    return db_filter_predicate


def set_permissions_from_filter(app, model, filter_query, change=True, delete=True):
    if change:
        rules.add_perm(
            '{app}.change_{model}'.format(
                app=app, model=model,
            ), get_predicate_from_filter(
                filter_query
            )
        )
    if delete:
        rules.add_perm(
            '{app}.delete_{model}'.format(
                app=app, model=model,
            ), get_predicate_from_filter(
                filter_query
            )
        )


class ObjectPermissionsModelAdmin(RulesObjectPermissionsModelAdmin):
    def get_filter_query(self, request):
        return None

    def get_queryset(self, request):
        fq = self.get_filter_query(request)
        qs = super(RulesObjectPermissionsModelAdmin, self).get_queryset(request)
        if fq is not None:
            qs = qs.filter(fq)
        return qs
