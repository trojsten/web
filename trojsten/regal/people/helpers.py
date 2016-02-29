from .models import User
from django.db import transaction


def get_similar_users(user):
    return User.objects.exclude(pk=user.pk).filter(
        first_name=user.first_name,
        last_name=user.last_name,
    )


@transaction.atomic
def merge_users(target_user, source_user, src_selected_fields, src_selected_user_props):
    print(src_selected_fields)
    print(src_selected_user_props)
    raise -1
