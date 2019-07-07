from django.core.files.storage import Storage
from django.db.models import Max


def get_noexisting_id(model):
    """
    Returns id for a model which is not yet in DB
    Currently works only with int IDs
    """
    max_id = model.objects.all().aggregate(Max("id"))["id__max"] or 0
    return max_id + 1


class TestNonFileSystemStorage(Storage):
    def __init__(self, prefix="http://example.com/"):
        self._files = set()
        self.prefix = prefix

    def add_file(self, name):
        self._files.add(name)

    def path(self, name):
        raise NotImplementedError

    def exists(self, name):
        return name in self._files

    def url(self, name):
        return "{}{}".format(self.prefix, name)
