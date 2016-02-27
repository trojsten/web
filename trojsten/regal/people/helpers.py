from .models import User


def get_similar_users(user):
    return User.objects.exclude(pk=user.pk).filter(
        first_name=user.first_name,
        last_name=user.last_name,
    )
