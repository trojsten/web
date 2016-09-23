# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models
from django.utils.encoding import force_text
from easy_select2.widgets import Select2Multiple

from .models import Thread


class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_sites')
    list_filter = ('sites', )
    formfield_overrides = {
        models.ManyToManyField: {'widget': Select2Multiple()}
    }

    def get_sites(self, obj):
        return ', '.join(force_text(x) for x in obj.sites.all())
    get_sites.short_description = 'domény'

admin.site.register(Thread, ThreadAdmin)
