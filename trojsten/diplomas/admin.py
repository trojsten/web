# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin

from easy_select2.widgets import Select2Multiple

from .widgets import Editor
from .models import DiplomaTemplate, DiplomaDataSource


class DiplomaTemplateAdminForm(forms.ModelForm):
    model = DiplomaTemplate

    class Meta:
        fields = '__all__'
        widgets = {
            'svg': Editor(mode='xml'),
            'sources': Select2Multiple
        }


class DiplomaTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    form = DiplomaTemplateAdminForm

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'sources':
            kwargs['initial'] = [x for x in DiplomaDataSource.objects.default()]
            return db_field.formfield(**kwargs)

        return super(DiplomaTemplateAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(DiplomaTemplate, DiplomaTemplateAdmin)
admin.site.register(DiplomaDataSource)
