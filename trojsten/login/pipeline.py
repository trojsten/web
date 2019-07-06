from trojsten.people.models import User


def associate_by_uid(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same uid in the DB.

    Use this pipeline only if you share the user db with provider.
    """
    if user:
        return None
    try:
        uid = details.get("id")
        user = backend.strategy.storage.user.get_user(uid)
        if user:
            return {"user": user}
    except User.DoesNotExist:
        return None
