# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from trojsten.menu.models import *


class MenuItemAdmin(admin.ModelAdmin):
    pass

admin.site.register(MenuItem, MenuItemAdmin)


class MenuGroupAdmin(admin.ModelAdmin):
    pass

admin.site.register(MenuGroup, MenuGroupAdmin)

