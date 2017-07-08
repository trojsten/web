# Caches history of KSP levels and provides minimal interface to access levels.
# When chache is invalidated, whole KSP history is generated anew.
# Supports updates with finished semester or camp.


def get_user_level_for_semester(user, semester):
    """Needed for access to a level of one user e.g. in task list view."""
    return 1


def get_users_levels_for_semester(users, semester):
    """Needed for results calculation -- use only few cache queries. """
    return {user: 1 for user in users}

