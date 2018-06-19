# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import DiplomaTemplate


class DiplomaTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


admin.site.register(DiplomaTemplate, DiplomaTemplateAdmin)
