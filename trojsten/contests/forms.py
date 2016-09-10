# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _


class TaskValidationForm(forms.ModelForm):
    def clean_category(self):
        if self.cleaned_data.get('round'):
            for category in self.cleaned_data.get('category'):
                if category.competition.id != self.cleaned_data.get('round').semester.competition.id:
                    raise forms.ValidationError(_("Category doesn't correspond with competition."), code='invalid')
        return self.cleaned_data.get('category')
