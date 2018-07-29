# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from easy_select2.widgets import Select2Multiple

from .models import DiplomaTemplate, DiplomaDataSource
from .widgets import Editor


class DiplomaTemplateAdminForm(forms.ModelForm):
    model = DiplomaTemplate

    class Meta:
        fields = '__all__'
        widgets = {
            'svg': Editor(mode='xml'),
            'sources': Select2Multiple,
            'authorized_groups': Select2Multiple
        }


class DiplomaTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_groups', 'get_sources')
    list_filter = ('name',)
    form = DiplomaTemplateAdminForm

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(DiplomaTemplateAdmin, self).get_queryset(request)
        user_groups = request.user.groups.all()
        return super(DiplomaTemplateAdmin, self).get_queryset(request).filter(
            authorized_groups__in=user_groups
        ).distinct()

    def get_groups(self, obj):
        return ', '.join(sorted(force_text(group) for group in obj.authorized_groups.all()))
    get_groups.short_description = _('authorized groups')

    def get_sources(self, obj):
        return ', '.join(sorted(x.name for x in obj.sources.all()))
    get_sources.short_description = _('sources')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'sources':
            kwargs['initial'] = [x for x in DiplomaDataSource.objects.default()]
            return db_field.formfield(**kwargs)

        return super(DiplomaTemplateAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(DiplomaTemplate, DiplomaTemplateAdmin)
admin.site.register(DiplomaDataSource)
