# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin

from .widgets import Editor
from .models import DiplomaTemplate


class DiplomaTemplateAdminForm(forms.ModelForm):
    model = DiplomaTemplate

    class Meta:
        fields = '__all__'
        widgets = {
            'svg': Editor(mode='xml'),
        }


class DiplomaTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    form = DiplomaTemplateAdminForm


admin.site.register(DiplomaTemplate, DiplomaTemplateAdmin)
