# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

from wiki.views import article


def contact_form_sent_redirect(request):
    messages.success(request, 'Vaša správa bola odoslaná. Ďakujeme za spätnú väzbu.')
    return redirect('/')


def home_redirect(request):
    if request.user.is_authenticated():
        if 'home' not in request.GET:
            return redirect(reverse('news_list', kwargs={'page': 1}))
    return article.ArticleView.as_view()(request, path='')


@login_required
def login_root_view(request):
    # @TODO: vymyslieť čo tu bude
    return render(request, 'trojsten/layout/main.html')
