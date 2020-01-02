from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _

from .models import Answer, Question, Vote
from collections import namedtuple


RatedAnswer = namedtuple('RatedAnswer', ['votes', 'text', 'pk'])


def view_question(request, pk=None):
    questions = Question.objects.filter(created_date__lte=timezone.now()).order_by("-created_date")
    if not questions:
        return render(
            request, "trojsten/polls/view_question.html", {"questions": None, "user": request.user}
        )
    if pk is None:
        pk = questions[0].pk
    current = get_object_or_404(Question, pk=pk)

    user = request.user
    if request.method == "POST":
        if not user.is_authenticated:
            messages.add_message(request, messages.ERROR, _("You need to sign in in order to vote."))
            return redirect("view_question", pk=pk)

        if current.expired:
            messages.add_message(
                request, messages.ERROR, _("This poll has already finished and no more voting is possible.")
            )
            return redirect("view_question", pk=pk)
        answer_pk = int(request.POST.get("action")[4:])
        answer = Answer.objects.filter(question=current, pk=answer_pk).first()
        if answer is None:
            messages.add_message(request, messages.ERROR, _("Invalid vote."))
            return redirect("view_question", pk=pk)

        Vote.objects.update_or_create(user=user, answer__question=current, defaults={'answer': answer})
        return redirect("view_question", pk=pk)

    given_votes = Vote.objects.filter(answer__question=current)
    user_vote = None if not user.is_authenticated else given_votes.filter(user=user).first()
    user_vote_pk = None if user_vote is None else user_vote.answer.pk
    answers = Answer.objects.filter(question=current)
    votes = {answer: 0 for answer in answers}
    for vote in given_votes:
        votes[vote.answer] += 1
    rated_answers = list(RatedAnswer(votes[answer], answer.text, answer.pk) for answer in votes)
    rated_answers.sort(reverse=True)
    return render(
        request,
        "trojsten/polls/view_question.html",
        {
            "questions": questions,
            "current": current,
            "votes": votes,
            "answers": rated_answers,
            "user_vote": user_vote_pk,
        },
    )
