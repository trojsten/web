from functools import reduce

from django.db import transaction

from trojsten.contests.models import Competition

from .models import User, UserProperty, UserPropertyKey


def get_similar_users(user):
    """Returns a list of users similar to the specified user."""
    return User.objects.exclude(pk=user.pk).filter(
        first_name=user.first_name, last_name=user.last_name
    )


@transaction.atomic
def merge_users(target_user, source_user, src_selected_fields, src_selected_user_prop_ids):
    """
    Merges source_user into target_user, replacing target_user's fields
    specified in src_selected_fields, and target_user's user_properties
    specified in src_selected_user_prop_ids.
    """
    for field in src_selected_fields:
        setattr(target_user, field, getattr(source_user, field))
    src_properties = source_user.get_properties()
    for prop in src_selected_user_prop_ids:
        key = UserPropertyKey.objects.get(pk=prop)
        if target_user.properties.filter(key=key).exists():
            if key in src_properties:
                user_prop = target_user.properties.get(key=key)
                user_prop.value = src_properties[key]
                user_prop.save()
            else:
                target_user.properties.get(key=key).delete()
        else:
            if key in src_properties:
                target_user.properties.create(key=key, value=src_properties[key])

    # Migrate all foreign key references from source object to target object.
    for related_field in filter(lambda f: f.one_to_many or f.one_to_one, User._meta.get_fields()):
        # skip user_properties, we have already handled them separately
        if related_field.related_model is UserProperty:
            continue
        # The variable name on the source_object model.
        src_varname = related_field.get_accessor_name()
        # The variable name on the related model.
        obj_varname = related_field.field.name
        if related_field.one_to_one:
            # If target object does not have this object set, we
            if getattr(target_user, src_varname, None) is None:
                obj = getattr(source_user, src_varname, None)
                if obj is not None:
                    obj.user = target_user
                    obj.save()
            # otherwise the object will be deleted when deleting the src_object
        else:
            related_objects = getattr(source_user, src_varname)
            for obj in related_objects.all():
                setattr(obj, obj_varname, target_user)
                obj.save()

    # Migrate all many to many references from source object to target object.
    for related_many_field in filter(
        lambda f: f.many_to_many, User._meta.get_fields(include_hidden=True)
    ):
        field_name = related_many_field.name
        related_many_objects = getattr(source_user, field_name).all()
        if related_many_objects:
            getattr(target_user, field_name).add(*related_many_objects)
            getattr(source_user, field_name).remove(*related_many_objects)

    source_user.delete()
    target_user.save()


def get_required_properties_by_competition(user):
    competitions = Competition.objects.current_site_only()
    competitions_action_required = filter(
        lambda c: not user.is_competition_ignored(c) and not user.is_valid_for_competition(c),
        competitions,
    )
    return {
        competition: set(competition.required_user_props.all())
        - set(map(lambda prop: prop.key, user.properties.all()))
        for competition in competitions_action_required
    }


def get_required_properties(user):
    # Merge all sets into one
    return reduce(lambda x, y: x | y, get_required_properties_by_competition(user).values(), set())
