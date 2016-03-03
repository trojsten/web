from .models import User, UserProperty, UserPropertyKey
from django.db import transaction


def get_similar_users(user):
    return User.objects.exclude(pk=user.pk).filter(
        first_name=user.first_name,
        last_name=user.last_name,
    )


@transaction.atomic
def merge_users(target_user, source_user, src_selected_fields, src_selected_user_prop_ids):
    for field in src_selected_fields:
        setattr(target_user, field, getattr(source_user, field))
    src_properties = source_user.get_properties()
    for prop in src_selected_user_prop_ids:
        if target_user.properties.filter(key__pk=prop).exists():
            if prop in src_properties:
                prop = target_user.properties.get(key__pk=prop)
                prop.value = src_properties[prop]
                prop.save()
            else:
                target_user.properties.get(key__pk=prop).delete()
        else:
            if prop in src_properties:
                key = UserPropertyKey.objects.get(pk=prop)
                target_user.properties.create(key=key, value=src_properties[prop])

    # Migrate all foreign key references from source object to target object.
    for related_object in source_user._meta.get_all_related_objects():
        # skip user_properties, we already handled them separately
        if related_object.related_model is UserProperty:
            continue
        # The variable name on the alias_object model.
        src_varname = related_object.get_accessor_name()
        # The variable name on the related model.
        obj_varname = related_object.field.name
        if related_object.one_to_one:
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
    for related_many_object in source_user._meta.get_all_related_many_to_many_objects():
        src_varname = related_many_object.get_accessor_name()
        obj_varname = related_many_object.field.name

        if src_varname is not None:
            # standard case
            related_many_objects = getattr(source_user, src_varname).all()
        else:
            # special case, symmetrical relation, no reverse accessor
            related_many_objects = getattr(source_user, obj_varname).all()
        for obj in related_many_objects.all():
            getattr(obj, obj_varname).remove(source_user)
            getattr(obj, obj_varname).add(target_user)

    source_user.delete()
    target_user.save()
