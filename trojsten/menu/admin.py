# -*- coding: utf-8 -*-

from django.contrib import admin

from trojsten.menu.models import MenuGroup, MenuItem


class MenuItemAdmin(admin.ModelAdmin):
    pass


admin.site.register(MenuItem, MenuItemAdmin)


class MenuGroupAdmin(admin.ModelAdmin):
    pass


admin.site.register(MenuGroup, MenuGroupAdmin)
