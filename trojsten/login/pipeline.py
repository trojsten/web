from trojsten.people.models import User


def associate_by_username(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same username in the DB.

    This pipeline entry is not 100% secure unless you have full control over the providers.
    """
    if user:
        return None
    try:
        username = details.get('username')
        user = backend.strategy.storage.user.get_user(username=username)
        print(username, user)
        if user:
            return {'user': user}
    except User.DoesNotExist:
        return None
