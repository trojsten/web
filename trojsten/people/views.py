from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from ksp_login.forms import UserProfileForm, get_profile_forms
from social.apps.django_app.default.models import UserSocialAuth

from trojsten.contests.models import Competition, Task, Round
from trojsten.people.models import User
from trojsten.reviews.helpers import edit_review
from trojsten.submit.constants import SUBMIT_TYPE_DESCRIPTION, SUBMIT_STATUS_IN_QUEUE,\
    SUBMIT_PAPER_FILEPATH, SUBMIT_STATUS_REVIEWED
from trojsten.submit.models import Submit
from .forms import SubmittedTasksForm, RoundSelectForm
from .models import UserProperty
from .constants import DEENVELOPING_NOT_REVIEWED_SYMBOL


class VisibleUserPropForm(forms.ModelForm):
    """Form with limited UserPropKeys."""

    def __init__(self, *args, **kwargs):
        super(VisibleUserPropForm, self).__init__(*args, **kwargs)
        self.fields['key'].queryset = self.fields['key'].queryset.filter(hidden=False)


def _get_user_props_formset(is_staff=False):
    form_class = forms.ModelForm if is_staff else VisibleUserPropForm

    return forms.inlineformset_factory(
        User, UserProperty,
        form=form_class,
        fields=('key', 'value'),
        widgets={
            'value': forms.widgets.Textarea(attrs={'class': 'col-sm-12 form-control', 'rows': 1})
        },
        extra=0,
    )


@login_required
def settings(request, settings_form=UserProfileForm):
    """
    Presents the user a form with their settings, basically the register
    form minus username minus password.
    Also presents additional app-specific forms listed in the
    KSP_LOGIN_PROFILE_FORMS setting to the user.
    """

    UserPropsFormSet = _get_user_props_formset(request.user.is_staff)

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


def submitted_tasks(request, user_pk, round_pk):
    user = get_object_or_404(User, pk=user_pk)
    round = get_object_or_404(Round, pk=round_pk)
    form = None
    if request.method == 'POST':
        round_form = RoundSelectForm(request.POST)
        if round_form.is_valid():
            round = round_form.cleaned_data['round']
        else:
            form = SubmittedTasksForm(round, request.POST)
            if form.is_valid():
                data = form.cleaned_data
                for task in Task.objects.filter(round=round):
                    value = data[str(task.number)]
                    if len(value) > 0:
                        points = 0 if value == DEENVELOPING_NOT_REVIEWED_SYMBOL else float(value)
                        status = SUBMIT_STATUS_IN_QUEUE if value == DEENVELOPING_NOT_REVIEWED_SYMBOL \
                            else SUBMIT_STATUS_REVIEWED
                        submit = Submit.objects.filter(
                            task=task,
                            user=user,
                            submit_type=SUBMIT_TYPE_DESCRIPTION,
                        ).order_by('-time').first()
                        if submit:
                            if value != DEENVELOPING_NOT_REVIEWED_SYMBOL:
                                submit.points = points
                                submit.testing_status = SUBMIT_STATUS_REVIEWED
                                submit.save()
                        else:
                            submit = Submit.objects.create(
                                task=task,
                                user=user,
                                submit_type=SUBMIT_TYPE_DESCRIPTION,
                                points=points,
                                filepath=SUBMIT_PAPER_FILEPATH,
                                testing_status=status,
                            )
                            submit.time = round.end_time + timezone.timedelta(seconds=-1)
                            submit.save()
                    else:
                        Submit.objects.filter(
                            task=task,
                            user=user,
                            submit_type=SUBMIT_TYPE_DESCRIPTION,
                            filepath=SUBMIT_PAPER_FILEPATH,
                        ).delete()
                return redirect('admin:people_user_change', user.pk)
    if not form:
        form = SubmittedTasksForm(round)
        for submit in Submit.objects.filter(task__round=round, user=user).order_by('time'):
            if submit.testing_status == SUBMIT_STATUS_REVIEWED:
                form.initial[str(submit.task.number)] = submit.points
            else:
                form.initial[str(submit.task.number)] = DEENVELOPING_NOT_REVIEWED_SYMBOL

    round_form = RoundSelectForm()
    round_form.initial['round'] = round
    context = {
        'round': round,
        'form': form,
        'round_form': round_form,
        'user': user
    }
    return render(
        request, 'admin/people/submitted_tasks.html', context
    )


def submitted_tasks_for_latest_round(request, user_pk):
    competition = Competition.objects.current_site_only().first()
    round = Round.objects.latest_finished_for_competition(competition)
    return submitted_tasks(request, user_pk, round.pk)
