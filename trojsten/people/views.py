from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from ksp_login.forms import UserProfileForm, get_profile_forms
from social.apps.django_app.default.models import UserSocialAuth

from trojsten.people.models import UserProperty
from .forms import UserPropsFormSet


@login_required
def settings(request, settings_form=UserProfileForm):
    """
    Presents the user a form with their settings, basically the register
    form minus username minus password.
    Also presents additional app-specific forms listed in the
    KSP_LOGIN_PROFILE_FORMS setting to the user.
    """
    form_classes = [settings_form] + get_profile_forms()

    forms = None
    user_props_form_set = None

    if request.method == "POST":
        if request.POST.get('user_props_submit', None):
            user_props_form_set = UserPropsFormSet(request.POST, instance=request.user)
            # @TODO(mio): check if user tries to set a hidden user_prop
            # @TODO(mio): enable creating new user props with existing, non hidden key
            if user_props_form_set.is_valid():
                user_props_form_set.save()
                return redirect('account_settings')
        else:
            forms = [form(request.POST, user=request.user)
                     for form in form_classes]
            if all(form.is_valid() for form in forms):
                for form in forms:
                    form.save()
                return redirect('account_settings')

    if not forms:
        forms = [form(user=request.user) for form in form_classes]
    if not user_props_form_set:
        user_props_form_set = UserPropsFormSet(
            instance=request.user, queryset=UserProperty.objects.visible(request.user)
        )

    return render(request, 'trojsten/people/settings.html', {
        'account_associations': UserSocialAuth.get_social_auth_for_user(request.user),
        'forms': forms,
        'user_props_form_set': user_props_form_set,
    })
