# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from wiki.views import article


def contact_form_sent_redirect(request):
    # Translators: original: Vaša správa bola odoslaná. Ďakujeme za spätnú väzbu.
    msg = _('Your message has been sent. Thank you for your feedback.')
    messages.success(request, msg)
    return redirect('/')


def home_redirect(request):
    if request.user.is_authenticated():
        if 'home' not in request.GET:
            return redirect(reverse('news_list', kwargs={'page': 1}))
    return article.ArticleView.as_view()(request, path='')
