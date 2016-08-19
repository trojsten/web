# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from wiki.views import article
from wiki.models import Article
from haystack.views import SearchView
from django.db.models import Q

def contact_form_sent_redirect(request):
    messages.success(request, 'Vaša správa bola odoslaná. Ďakujeme za spätnú väzbu.')
    return redirect('/')


def home_redirect(request):
    if request.user.is_authenticated():
        if 'home' not in request.GET:
            return redirect(reverse('news_list', kwargs={'page': 1}))
    return article.ArticleView.as_view()(request, path='')


#Custom view for haystack SearchView
class CustomSearchView(SearchView):
    request = None

    #filer results according to read permissions of user
    def get_results(self):
        qs = super(CustomSearchView, self).get_results()
        user = self.request.user
        if user.is_superuser:
            return qs
        public = qs.filter(other_read=True)
        groups = [g.id for g in user.groups.all()]
        return qs.filter(group__in=groups) | public
