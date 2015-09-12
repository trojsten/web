# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy

from easy_select2.widgets import Select2Multiple

from .models import *


class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_sites')
    list_filter = ('sites', )
    formfield_overrides = {
        models.ManyToManyField: {'widget': Select2Multiple()}
    }

    def get_sites(self, obj):
        return ', '.join(force_text(x) for x in obj.sites.all())
    # Translators: original: domény
    get_sites.short_description = ugettext_lazy('domains')

admin.site.register(Thread, ThreadAdmin)
