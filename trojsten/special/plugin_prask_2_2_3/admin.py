# -*- coding: utf-8 -*-

from django.contrib import admin
from easy_select2 import select2_modelform

from .models import UserLink


class UserLinkAdmin(admin.ModelAdmin):
    form = select2_modelform(UserLink)
    list_display = ('user', 'link')


admin.site.register(UserLink, UserLinkAdmin)
