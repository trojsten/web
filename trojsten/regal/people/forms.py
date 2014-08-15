from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from trojsten.regal.people.models import User
from django.utils.translation import string_concat, ugettext_lazy as _
from social.apps.django_app.utils import setting
from ksp_login import SOCIAL_AUTH_PARTIAL_PIPELINE_KEY

class TrojstenUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date', 'gender', 'school', 'graduation',)
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
            pipeline_state = request.session[setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY',
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

    def get_initial_from_pipeline(self, pipeline_state):
        return None if not pipeline_state else {
            'username': pipeline_state['details']['username'],
            'first_name': pipeline_state['details']['first_name'],
            'last_name': pipeline_state['details']['last_name'],
            'email': pipeline_state['details']['email'],
        }

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
    
    def save(self, commit=True):
        user = super(TrojstenUserCreationForm, self).save(commit=False)        
        user.set_password(self.cleaned_data['password1'])
        if not (self.cleaned_data.get('password1') or self.password_required):
            user.set_unusable_password()
        if commit:
            user.save()
        return user

class TrojstenUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    class Meta:
        model = User

    def clean_password(self):
        return self.initial['password']

