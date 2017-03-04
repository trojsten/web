from django import template

from trojsten.contests.models import Competition

register = template.Library()


@register.inclusion_tag('trojsten/people/parts/additional_registration.html', takes_context=True)
def show_competition_registration(context):
    user = context.request.user
    if user.is_anonymous():
        return context

    competitions = Competition.objects.current_site_only()
    competitions_action_required = filter(
        lambda c: not user.is_competition_ignored(c) and not user.is_valid_for_competition(c),
        competitions,
    )
    required_properties_by_competition = {
        competition: set(competition.required_user_props.all()) - set(user.properties.all())
        for competition in competitions_action_required
    }

    context['required_properties_by_competition'] = required_properties_by_competition
    return context
