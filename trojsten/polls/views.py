from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Answer, Question, Vote


def view_question(request, pk=None):
    questions = Question.objects.filter(created_date__lte=timezone.now()).order_by("-created_date")
    if not questions:
        return render(
            request, "trojsten/polls/view_question.html", {"questions": [], "user": request.user}
        )
    if pk is None:
        pk = questions[0].pk
    current = get_object_or_404(Question, pk=pk)
    current.expired = current.deadline <= timezone.now()

    user = request.user
    if request.method == "POST":
        if not user.is_authenticated:
            # You must be logged in
            messages.add_message(request, messages.ERROR, "Pre hlasovanie sa musíš prihlásiť.")
            return redirect("view_question", pk=pk)

        answer_pk = int(request.POST.get("action")[4:])
        if current.expired:
            # Deadline is over
            messages.add_message(
                request, messages.ERROR, "V tejto ankete už nie je možné hlasovať."
            )
            return redirect("view_question", pk=pk)
        answer = Answer.objects.filter(question=current, pk=answer_pk).first()
        if answer is None:
            # Invalid vote
            messages.add_message(request, messages.ERROR, "Neplatný hlas.")
            return redirect("view_question", pk=pk)

        existing = Vote.objects.filter(user=user, answer__question=current)
        if existing:
            existing[0].answer = answer
            existing[0].save()
            for e in existing[1:]:  # This shouldn't happen (user having two votes)
                e.delete()
        else:
            Vote.objects.create(user=user, answer=answer)
        return redirect("view_question", pk=pk)

    given_votes = Vote.objects.filter(answer__question=current)
    user_vote = None if not user.is_authenticated else given_votes.filter(user=user).first()
    user_vote_pk = None if user_vote is None else user_vote.answer.pk
    answers = Answer.objects.filter(question=current)
    votes = {answer: 0 for answer in answers}
    for vote in given_votes:
        votes[vote.answer] += 1
    zipped = list((votes[answer], answer.text, answer.pk) for answer in votes)
    zipped.sort(reverse=True)
    return render(
        request,
        "trojsten/polls/view_question.html",
        {
            "questions": questions,
            "current": current,
            "votes": votes,
            "answers": zipped,
            "user_vote": user_vote_pk,
            "range2": range(2),
        },
    )
