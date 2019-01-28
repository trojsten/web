from django import template

from trojsten.people.helpers import get_required_properties_by_competition

register = template.Library()


@register.inclusion_tag('trojsten/people/parts/additional_registration.html', takes_context=True)
def show_competition_registration(context):
    user = context.request.user
    if user.is_anonymous:
        return context

    context['required_properties_by_competition'] = get_required_properties_by_competition(user)
    return context
