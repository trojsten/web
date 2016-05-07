from django.db.models import Max


def get_noexisting_id(model):
    """
    Returns id for a model which is not yet in DB
    Currently works only with int IDs
    """
    max_id = model.objects.all().aggregate(Max('id'))['id__max'] or 0
    return max_id + 1
