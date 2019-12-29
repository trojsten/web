from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from .models import Question, Answer, Vote

from datetime import datetime


def create_default_questions():
    q = Question(text = "Čo znamená skratka LTT?",
                deadline = datetime(2018, 12, 31, 23, 59, 59),
                answers = "Lacná trápna taška\nLen trochu tuniaka\nLietam tam tiež",
                answer_count = 3)
    q.save()
    q = Question(text = "Ktorý je najlepší programovací jazyk?",
                answers = "Predsa HTML\nJava\nJavaScript\nRuby\nPython\nC\nC++\nPascal", answer_count = 8)
    q.save()


def view_question(request, pk=None):
    questions = Question.objects.filter(created_date__lte = timezone.now()).order_by('-created_date')
    if not questions:
        return render(request, 'trojsten/polls/view_question.html', {'questions': [], 'user': request.user})
        #create_default_questions()
        #questions = Question.objects.filter(created_date__lte = timezone.now()).order_by('-created_date')
    if pk is None:
        pk = questions[0].pk
    current = get_object_or_404(Question, pk=pk)
    current.expired = current.deadline<=timezone.now()
    
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            # You must be logged in
            messages.add_message(request, messages.ERROR, "Pre hlasovanie sa musíš prihlásiť.")
            return redirect('view_question', pk=pk)
        
        answer_pk = int(request.POST.get("action")[4:])
        if current.expired:
            # Deadline is over
            messages.add_message(request, messages.ERROR, "V tejto ankete už nie je možné hlasovať.")
            return redirect('view_question', pk=pk)
        answer = Answer.objects.filter(question=current, pk=answer_pk).first()
        if answer is None:
            #Invalid vote
            messages.add_message(request, messages.ERROR, "Neplatný hlas.")
            return redirect('view_question', pk=pk)
        
        existing = Vote.objects.filter(user=user, answer__question=current)
        if existing:
            existing[0].answer = answer
            existing[0].save()
            for e in existing[1:]: #This shouldn't happen (user having two votes)
                e.delete()
        else:
            Vote.objects.create(user=user, answer=answer)
        return redirect('view_question', pk=pk)
    
    given_votes = Vote.objects.filter(answer__question=current)
    answers = Answer.objects.filter(question=current)
    votes = {answer: 0 for answer in answers}
    for vote in given_votes:
        votes[vote.answer] += 1
    zipped = list((votes[answer], answer.text, answer.pk) for answer in votes)
    zipped.sort(reverse=True)
    return render(request, 'trojsten/polls/view_question.html', {'questions': questions, 'current': current, 'votes': votes, 'answers': zipped})