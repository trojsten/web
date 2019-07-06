from django.conf import settings
from django.db import models

from .algorithms import ALL


class UserCategory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    category = models.CharField(max_length=1)
    points = models.IntegerField(default=0)
    state = models.CharField(max_length=256, default="")

    class Meta:
        unique_together = ("user", "category")


class Visit(models.Model):
    user_category = models.ForeignKey(UserCategory, related_name="visits", on_delete=models.CASCADE)
    number = models.IntegerField()
    response = models.IntegerField()

    def formatted_response(self):
        return ALL[self.user_category.category].format(self.response)
