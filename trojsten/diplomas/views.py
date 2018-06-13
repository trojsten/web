from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def diploma_participants_submit_post(request, task_id, submit_type):
    pass


def view_diplomas(request):
    context = None
    return render(
        request, 'trojsten/diplomas/view_diplomas.html', context
    )