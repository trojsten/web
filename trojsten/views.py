# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import redirect


def contact_form_sent_redirect(request):
    messages.success(request, 'Vaša správa bola odoslaná. Ďakujeme za spätnú väzbu.')
    return redirect('/')
