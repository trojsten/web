# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import string_concat, ugettext_lazy as _

from datetime import date

from ksp_login import SOCIAL_AUTH_PARTIAL_PIPELINE_KEY
from social.apps.django_app.utils import setting
from easy_select2.widgets import Select2

from trojsten.regal.people.models import User, Address
from . import constants


class TrojstenUserBaseForm(forms.ModelForm):
    required_css_class = 'required'
    street = forms.CharField(max_length=70, label='Ulica')
    town = forms.CharField(max_length=64, label='Mesto')
    postal_code = forms.CharField(
        max_length=16, label='PSČ')
    country = forms.CharField(
        max_length=32, label='Krajina')

    has_correspondence_address = forms.BooleanField(
        label="Korešpondenčná adresa",
        required=False,
        help_text="Zaškrtni, ak chceš aby sme ti poštu posielali "
        "inde ako domov.(Typicky, ak bývaš na internáte.)"
    )

    corr_street = forms.CharField(max_length=70, label='Ulica', required=False)
    corr_town = forms.CharField(max_length=64, label='Mesto', required=False)
    corr_postal_code = forms.CharField(
        max_length=16, label='PSČ', required=False)
    corr_country = forms.CharField(
        max_length=32, label='Krajina', required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'birth_date', 'gender', 'school', 'graduation',)
        widgets = {
            'school': Select2(),
        }

    def __init__(self, *args, **kwargs):
        super(TrojstenUserBaseForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['gender'] = forms.ChoiceField(
            widget=forms.RadioSelect,
            label='Pohlavie',
            choices=User.GENDER_CHOICES,
        )

    def get_initial_from_pipeline(self, pipeline_state):
        return None if not pipeline_state else {
            'username': pipeline_state['details']['username'],
            'first_name': pipeline_state['details']['first_name'],
            'last_name': pipeline_state['details']['last_name'],
            'email': pipeline_state['details']['email'],
        }

    def clean_email(self):
        if len(self.cleaned_data.get('email')) == 0:
            raise forms.ValidationError(
                _("This field is required."),
                code="email_required",
            )
        return self.cleaned_data.get('email')

    def clean_first_name(self):
        if len(self.cleaned_data.get('first_name')) == 0:
            raise forms.ValidationError(
                _("This field is required."),
                code="first_name_required",
            )
        return self.cleaned_data.get('first_name')

    def clean_last_name(self):
        if len(self.cleaned_data.get('last_name')) == 0:
            raise forms.ValidationError(
                _("This field is required."),
                code="last_name_required",
            )
        return self.cleaned_data.get('last_name')

    def clean_corr_street(self):
        if self.cleaned_data.get('has_correspondence_address'):
            if len(self.cleaned_data.get('corr_street')) == 0:
                raise forms.ValidationError(
                    _("This field is required."),
                    code="corr_street_required",
                )

        return self.cleaned_data.get('corr_street')

    def clean_corr_town(self):
        if self.cleaned_data.get('has_correspondence_address'):
            if len(self.cleaned_data.get('corr_town')) == 0:
                raise forms.ValidationError(
                    _("This field is required."),
                    code="corr_town_required",
                )

        return self.cleaned_data.get('corr_town')

    def clean_corr_postal_code(self):
        if self.cleaned_data.get('has_correspondence_address'):
            if len(self.cleaned_data.get('corr_postal_code')) == 0:
                raise forms.ValidationError(
                    _("This field is required."),
                    code="corr_postal_code_required",
                )

        return self.cleaned_data.get('corr_postal_code')

    def clean_corr_country(self):
        if self.cleaned_data.get('has_correspondence_address'):
            if len(self.cleaned_data.get('corr_country')) == 0:
                raise forms.ValidationError(
                    _("This field is required."),
                    code="corr_country_required",
                )

        return self.cleaned_data.get('corr_country')

    def clean_graduation(self):
        grad = int(self.cleaned_data.get('graduation'))

        if grad < constants.GRADUATION_YEAR_MIN:
            raise forms.ValidationError(
                _("Your graduation year is too far in the past."),
                code="graduation_too_soon",
            )

        if grad > date.today().year + constants.GRADUATION_YEAR_MAX_AHEAD:
            raise forms.ValidationError(
                _("Your graduation year is too far in the future."),
                code="graduation_too_late",
            )

        return grad


class TrojstenUserChangeForm(TrojstenUserBaseForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        self.user = user
        if user:
            kwargs['instance'] = self.user
            if self.user.home_address:
                kwargs['initial'] = {
                    'street': user.home_address.street,
                    'town': user.home_address.town,
                    'postal_code': user.home_address.postal_code,
                    'country': user.home_address.country,
                }
            if user.mailing_address:
                kwargs['initial']['corr_street'] = user.mailing_address.street
                kwargs['initial']['corr_town'] = user.mailing_address.town
                kwargs['initial'][
                    'corr_postal_code'] = user.mailing_address.postal_code
                kwargs['initial'][
                    'corr_country'] = user.mailing_address.country
                kwargs['initial']['has_correspondence_address'] = True

        super(TrojstenUserChangeForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(TrojstenUserChangeForm, self).save(commit)
        street = self.cleaned_data.get('street')
        town = self.cleaned_data.get('town')
        postal_code = self.cleaned_data.get('postal_code')
        country = self.cleaned_data.get('country')

        has_correspondence_address = self.cleaned_data.get(
            'has_correspondence_address')
        corr_street = self.cleaned_data.get('corr_street')
        corr_town = self.cleaned_data.get('corr_town')
        corr_postal_code = self.cleaned_data.get('corr_postal_code')
        corr_country = self.cleaned_data.get('corr_country')

        if has_correspondence_address:
            if not user.mailing_address:
                corr_address = Address(
                    street=corr_street, town=corr_town, postal_code=corr_postal_code, country=corr_country)
            else:
                user.mailing_address.street = corr_street
                user.mailing_address.town = corr_town
                user.mailing_address.postal_code = corr_postal_code
                user.mailing_address.country = corr_country

        ## Note: Only case when user does not have home address is when that user has been created by
        ## django management commands (manage.py)
        if not user.home_address:
            home_address = Address(
                street=street, town=town, postal_code=postal_code, country=country)
        else:
            user.home_address.street = street
            user.home_address.town = town
            user.home_address.postal_code = postal_code
            user.home_address.country = country

        if commit:
            ## Warning: if commit==False, home address object for user is not created and assigned if user
            ## does not already have one (although such users should be extremely rare)..
            if not user.home_address:
                home_address.save()
                user.home_address = home_address
            else:
                user.home_address.save()
            if user.mailing_address and not has_correspondence_address:
                user.mailing_address = None
            if has_correspondence_address and not user.mailing_address:
                corr_address.save()
                user.mailing_address = corr_address
            user.save()

        return self


class TrojstenUserCreationForm(TrojstenUserBaseForm):
    password1 = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"), widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'birth_date', 'gender', 'school', 'graduation',)
        widgets = {
            'school': forms.Select(attrs={'class': 'autocomplete'}),
        }

    def __init__(self, *args, **kwargs):
        try:
            request = kwargs['request']
            del kwargs['request']
        except KeyError:
            raise TypeError("Argument 'request' missing.")
        try:
            pipeline_state = request.session[setting(
                'SOCIAL_AUTH_PARTIAL_PIPELINE_KEY',
                                                     SOCIAL_AUTH_PARTIAL_PIPELINE_KEY)]
            pipeline_state = pipeline_state['kwargs']
            self.password_required = False
        except KeyError:
            self.password_required = True
            pipeline_state = None
        if not args and 'initial' not in kwargs:
            kwargs['initial'] = self.get_initial_from_pipeline(pipeline_state)

        super(TrojstenUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['password1'].help_text = _(
            "We recommend choosing a strong passphrase but we don't "
            "enforce any ridiculous constraints on your passwords."
        )

        if not self.password_required:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].help_text = string_concat(_(
                "Since you're logging in using an external provider, "
                "this field is optional; however, by supplying it, you "
                "will be able to log in using a password. "
            ), self.fields['password1'].help_text)

    def clean_password2_default(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                _("The two password fields didn't match."),
                code='password_mismatch',
            )
        return password2

    def clean_password2(self):
        if (self.password_required or self.cleaned_data.get('password1') or
                self.cleaned_data.get('password2')):
            return self.clean_password2_default()
        return None

    def save(self, commit=True):
        user = super(TrojstenUserCreationForm, self).save(commit=False)

        user.set_password(self.cleaned_data['password1'])
        if not (self.cleaned_data.get('password1') or self.password_required):
            user.set_unusable_password()

        street = self.cleaned_data.get('street')
        town = self.cleaned_data.get('town')
        postal_code = self.cleaned_data.get('postal_code')
        country = self.cleaned_data.get('country')

        has_correspondence_address = self.cleaned_data.get(
            'has_correspondence_address')
        corr_street = self.cleaned_data.get('corr_street')
        corr_town = self.cleaned_data.get('corr_town')
        corr_postal_code = self.cleaned_data.get('corr_postal_code')
        corr_country = self.cleaned_data.get('corr_country')

        main_address = Address(
            street=street, town=town, postal_code=postal_code, country=country)

        if has_correspondence_address:
            corr_address = Address(
                street=corr_street, town=corr_town, postal_code=corr_postal_code, country=corr_country)

        if commit:
            main_address.save()
            user.home_address = main_address
            if has_correspondence_address:
                corr_address.save()
                user.mailing_address = corr_address
            user.save()
        return user
