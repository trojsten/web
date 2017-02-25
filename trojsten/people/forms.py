# -*- coding: utf-8 -*-
from collections import OrderedDict

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from ksp_login import SOCIAL_AUTH_PARTIAL_PIPELINE_KEY
from social.apps.django_app.utils import setting

from trojsten.contests.models import Task, Round, Competition
from trojsten.people.models import Address, DuplicateUser, User

from . import constants
from .helpers import get_similar_users


class TrojstenUserBaseForm(forms.ModelForm):
    required_css_class = 'required'
    street = forms.CharField(max_length=70, label=_('Street'))
    town = forms.CharField(max_length=64, label=_('Town'))
    postal_code = forms.CharField(
        max_length=16, label=_('Postal code'))
    country = forms.CharField(
        max_length=32, label=_('Country'))

    MAILING_OPTION_CHOICES = [
        (constants.MAILING_OPTION_HOME, _('home')),
        (constants.MAILING_OPTION_SCHOOL, _('school')),
        (constants.MAILING_OPTION_OTHER, _('other address (e. g. to a dormitory)'))
    ]
    mailing_option = forms.ChoiceField(
        required=True, choices=MAILING_OPTION_CHOICES,
        label=_("Correspondence address"), widget=forms.RadioSelect,
        help_text=_("Choose, where you want to accept mails."),
        initial=constants.MAILING_OPTION_HOME
    )

    corr_street = forms.CharField(max_length=70, label=_('Street'), required=False)
    corr_town = forms.CharField(max_length=64, label=_('Town'), required=False)
    corr_postal_code = forms.CharField(
        max_length=16, label=_('Postal code'), required=False)
    corr_country = forms.CharField(
        max_length=32, label=_('Country'), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'birth_date', 'gender', 'school', 'graduation',)
        widgets = {
            'school': forms.Select(attrs={'class': 'autocomplete'}),
        }

    def __init__(self, *args, **kwargs):
        super(TrojstenUserBaseForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['gender'] = forms.ChoiceField(
            widget=forms.RadioSelect,
            label=_('Gender'),
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
        if self.cleaned_data.get('mailing_option') == constants.MAILING_OPTION_OTHER:
            if len(self.cleaned_data.get('corr_street')) == 0:
                raise forms.ValidationError(
                    _("This field is required."),
                    code="corr_street_required",
                )

        return self.cleaned_data.get('corr_street')

    def clean_corr_town(self):
        if self.cleaned_data.get('mailing_option') == constants.MAILING_OPTION_OTHER:
            if len(self.cleaned_data.get('corr_town')) == 0:
                raise forms.ValidationError(
                    _("This field is required."),
                    code="corr_town_required",
                )

        return self.cleaned_data.get('corr_town')

    def clean_corr_postal_code(self):
        if self.cleaned_data.get('mailing_option') == constants.MAILING_OPTION_OTHER:
            if len(self.cleaned_data.get('corr_postal_code')) == 0:
                raise forms.ValidationError(
                    _("This field is required."),
                    code="corr_postal_code_required",
                )

        return self.cleaned_data.get('corr_postal_code')

    def clean_corr_country(self):
        if self.cleaned_data.get('mailing_option') == constants.MAILING_OPTION_OTHER:
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

        if grad > timezone.localtime(timezone.now()).year + constants.GRADUATION_YEAR_MAX_AHEAD:
            raise forms.ValidationError(
                _("Your graduation year is too far in the future."),
                code="graduation_too_late",
            )

        return grad

    def clean_mailing_option(self):
        school = self.cleaned_data.get('school')
        option = self.cleaned_data.get('mailing_option')
        if option == constants.MAILING_OPTION_SCHOOL and \
                (school is None or school.pk == constants.OTHER_SCHOOL_ID):
            raise forms.ValidationError(
                _("We cannot send you correspondence to school when you don't choose any school. "
                  "If your school is not in the list "
                  "write us in an e-mail that you want us to send correspodence to school"),
                code='no_school_to_mail'
            )
        return option


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
                    'mailing_option': user.get_mailing_option(),
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

        corr_street = self.cleaned_data.get('corr_street')
        corr_town = self.cleaned_data.get('corr_town')
        corr_postal_code = self.cleaned_data.get('corr_postal_code')
        corr_country = self.cleaned_data.get('corr_country')

        mailing_option = self.cleaned_data.get('mailing_option', constants.MAILING_OPTION_HOME)
        has_correspondence_address = mailing_option == constants.MAILING_OPTION_OTHER
        user.mail_to_school = (mailing_option == constants.MAILING_OPTION_SCHOOL)

        if has_correspondence_address:
            if not user.mailing_address:
                corr_address = Address(
                    street=corr_street,
                    town=corr_town,
                    postal_code=corr_postal_code,
                    country=corr_country,
                )
            else:
                user.mailing_address.street = corr_street
                user.mailing_address.town = corr_town
                user.mailing_address.postal_code = corr_postal_code
                user.mailing_address.country = corr_country

        # Note: Only case when user does not have home address is when that user has been created by
        # django management commands (manage.py)
        if not user.home_address:
            home_address = Address(
                street=street, town=town, postal_code=postal_code, country=country)
        else:
            user.home_address.street = street
            user.home_address.town = town
            user.home_address.postal_code = postal_code
            user.home_address.country = country

        if commit:
            # Warning: if commit==False, home address object for user is not created and assigned
            # if user does not already have one (although such users should be extremely rare)..
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
            if not DuplicateUser.objects.filter(user=user).exists():
                similar_users = get_similar_users(user)
                if len(similar_users):
                    DuplicateUser.objects.create(user=user)

        return user


class TrojstenUserCreationForm(TrojstenUserBaseForm):
    password1 = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification.")
    )

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
                SOCIAL_AUTH_PARTIAL_PIPELINE_KEY,
            )]
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

        mailing_option = self.cleaned_data.get('mailing_option', constants.MAILING_OPTION_HOME)
        has_correspondence_address = mailing_option == constants.MAILING_OPTION_OTHER
        user.mail_to_school = mailing_option == constants.MAILING_OPTION_SCHOOL

        corr_street = self.cleaned_data.get('corr_street')
        corr_town = self.cleaned_data.get('corr_town')
        corr_postal_code = self.cleaned_data.get('corr_postal_code')
        corr_country = self.cleaned_data.get('corr_country')

        main_address = Address(
            street=street, town=town, postal_code=postal_code, country=country)

        if has_correspondence_address:
            corr_address = Address(
                street=corr_street,
                town=corr_town,
                postal_code=corr_postal_code,
                country=corr_country,
            )

        if commit:
            main_address.save()
            user.home_address = main_address
            if has_correspondence_address:
                corr_address.save()
                user.mailing_address = corr_address
            user.save()
            similar_users = get_similar_users(user)
            if len(similar_users):
                DuplicateUser.objects.create(user=user)
        return user


class MergeFieldFactory:
    def __init__(self, user, candidate):
        self.user = user
        self.candidate = candidate
        self.props = {
            self.user: self.user.get_properties(),
            self.candidate: self.candidate.get_properties(),
        }

    def get_field(self, key, display=False, use_datetime=False):
        def get_choice(user):
            return (
                user.pk,
                getattr(user, 'get_%s_display' % (key,))() if display
                else getattr(user, key)
            )

        return forms.ChoiceField(
            label=_(key),
            choices=[get_choice(self.user), get_choice(self.candidate)],
            widget=forms.RadioSelect,
            initial=self.candidate.pk,
        )

    def get_prop_field(self, key):
        def get_choice(user):
            return (
                user.pk,
                self.props[user].get(key, None),
            )

        return forms.ChoiceField(
            label=key.key_name,
            choices=[get_choice(self.user), get_choice(self.candidate)],
            widget=forms.RadioSelect,
            initial=self.candidate.pk,
        )


class MergeForm(forms.Form):
    def __init__(self, user, candidate, *args, **kwargs):
        super(MergeForm, self).__init__(*args, **kwargs)
        self.user = user
        self.candidate = candidate

        field_factory = MergeFieldFactory(user, candidate)
        user_fields = [field.name for field in User._meta.get_fields() if not field.is_relation]
        display = set(['gender'])
        use_datetime = set(['last_login', 'date_joined', 'birth_date'])
        prop_keys = set(user.get_properties().keys()) | set(candidate.get_properties().keys())

        self.fields.update(OrderedDict([
            (
                f,
                field_factory.get_field(f, display=f in display, use_datetime=f in use_datetime)
            ) for f in user_fields
        ] + [
            (
                '%s%s' % (constants.USER_PROP_PREFIX, prop_key.pk),
                field_factory.get_prop_field(prop_key)
            ) for prop_key in prop_keys
        ]))


class SubmittedTasksFrom(forms.Form):

    def __init__(self, *args, **kwargs):
        round = kwargs.pop('round')
        super(SubmittedTasksFrom, self).__init__(*args, **kwargs)
        for task in Task.objects.filter(round=round).order_by('number'):
            self.fields[str(task.number)] = forms.BooleanField(required=False)


class RoundSelectForm(forms.Form):
    round = forms.ModelChoiceField(
            label=_('Round'),
            queryset=Round.objects.filter(
                semester__competition__in=Competition.objects.current_site_only()
            ).order_by('-end_time'),
            initial=round
    )
