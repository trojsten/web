# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from wiki.views import article
from wiki.views.article import SearchView
from wiki import models

def contact_form_sent_redirect(request):
    messages.success(request, 'Vaša správa bola odoslaná. Ďakujeme za spätnú väzbu.')
    return redirect('/')


def home_redirect(request):
    if request.user.is_authenticated():
        if 'home' not in request.GET:
            return redirect(reverse('news_list', kwargs={'page': 1}))
    return article.ArticleView.as_view()(request, path='')

class WikiSearchView(SearchView):
    def get_queryset(self):
        articles = super(WikiSearchView, self).get_queryset()
        return articles.filter(urlpath__site_id=6)