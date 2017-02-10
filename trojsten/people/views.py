from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from ksp_login.forms import UserProfileForm, get_profile_forms
from social.apps.django_app.default.models import UserSocialAuth

from trojsten.people.models import User, UserProperty

from .models import UserProperty


class VisibleUserPropForm(forms.ModelForm):
    """Form with limited UserPropKeys."""

    def __init__(self, *args, **kwargs):
        super(VisibleUserPropForm, self).__init__(*args, **kwargs)
        self.fields['key'].queryset = self.fields['key'].queryset.filter(hidden=False)


@login_required
def settings(request, settings_form=UserProfileForm):
    """
    Presents the user a form with their settings, basically the register
    form minus username minus password.
    Also presents additional app-specific forms listed in the
    KSP_LOGIN_PROFILE_FORMS setting to the user.
    """

    form_class = forms.ModelForm if request.user.is_staff else VisibleUserPropForm

    UserPropsFormSet = forms.inlineformset_factory(
        User, UserProperty,
        form=form_class,
        fields=('key', 'value'),
        widgets={
            'value': forms.widgets.Textarea(attrs={'class': 'col-sm-12 form-control', 'rows': 1})
        },
        extra=0,
    )

    form_classes = [settings_form] + get_profile_forms()

    _forms = None
    user_props_form_set = None

    if request.method == "POST":
        if request.POST.get('user_props_submit', None):
            user_props_form_set = UserPropsFormSet(request.POST, instance=request.user)
            if user_props_form_set.is_valid():
                user_props_form_set.save()
                return redirect(reverse('account_settings') + '#props')
        else:
            _forms = [form(request.POST, user=request.user)
                      for form in form_classes]
            if all(form.is_valid() for form in _forms):
                for form in _forms:
                    form.save()
                return redirect('account_settings')

    if not _forms:
        _forms = [form(user=request.user) for form in form_classes]
    if not user_props_form_set:
        user_props_form_set = UserPropsFormSet(
            instance=request.user, queryset=UserProperty.objects.visible(request.user)
        )

    return render(request, 'trojsten/people/settings.html', {
        'account_associations': UserSocialAuth.get_social_auth_for_user(request.user),
        'forms': _forms,
        'user_props_form_set': user_props_form_set,
    })
