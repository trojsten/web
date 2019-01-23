from django.conf import settings
from django.db import models


class UserLevel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)
    level_id = models.IntegerField()
    try_count = models.IntegerField(default=0)
    solved = models.BooleanField(default=False)

    MAX_TRY_COUNT = 50

    def add_try(self, input, output):
        self.try_count += 1
        self.save()
        new_try = Try(userlevel=self, input=str(input), output=output)
        new_try.save()
        if self.try_count > UserLevel.MAX_TRY_COUNT:
            self.try_set.order_by('id')[0].delete()

    class Meta:
        unique_together = (("user", "level_id"),)


class Try(models.Model):
    userlevel = models.ForeignKey('UserLevel', on_delete=models.CASCADE)
    input = models.CharField(max_length=15)
    output = models.CharField(max_length=30)
