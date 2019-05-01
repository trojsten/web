from django_nyt.utils import subscribe
from django_nyt.models import Settings
from django.contrib.contenttypes.models import ContentType

def subscribe_user_auto(user, key, target=None):
    subscribe(Settings.get_default_setting(user), key, content_type=ContentType.objects.get_for_model(target), object_id=target.id)