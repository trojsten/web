from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _


def after_30_days():
    now = timezone.now()
    end = now + timedelta(days=30)
    return end.replace(hour=23, minute=59, second=59)


class Question(models.Model):
    text = models.CharField(max_length=1000)
    created_date = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField(default=after_30_days)

    @property
    def expired(self):
        return self.deadline <= timezone.now()

    def __str__(self):
        return self.text


class Answer(models.Model):
    text = models.CharField(max_length=1000)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)

    def __str__(self):
        return _('Answer "{answer}" to question "{question}"').format(
            answer=self.text, question=str(self.question)
        )


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE)

    def __str__(self):
        return _("Vote for {answer}").format(answer=str(self.answer))

    def validate_unique(self, *args, **kwargs):
        super(Vote, self).validate_unique(*args, **kwargs)

        if self.__class__.objects.filter(
            answer__question=self.answer.question, user=self.user
        ).exists():
            raise ValidationError(
                message=_("A vote of this user for this question already exists."),
                code="vote.validate_unique",
            )
