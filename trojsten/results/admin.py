# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from easy_select2 import select2_modelform

from .models import Results


class ResultsAdmin(admin.ModelAdmin):
    form = select2_modelform(Results)
    list_display = ('round', 'tag', 'is_single_round', 'has_previous_results', 'time', )


admin.site.register(Results, ResultsAdmin)
