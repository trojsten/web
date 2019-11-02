# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from haystack.views import SearchView
from wiki.views import article


def contact_form_sent_redirect(request):
    messages.success(request, "Vaša správa bola odoslaná. Ďakujeme za spätnú väzbu.")
    return redirect("contact_form")


def home_redirect(request):
    if request.user.is_authenticated:
        if "home" not in request.GET:
            return redirect(reverse("dashboard"))

    return article.ArticleView.as_view()(request, path="")


# Custom view for haystack SearchView
class CustomSearchView(SearchView):
    request = None

    # filer results according to read permissions of user
    def get_results(self):
        qs = super(CustomSearchView, self).get_results()
        user = self.request.user
        if user.is_superuser:
            return qs
        public = qs.filter(other_read=True)
        groups = [g.id for g in user.groups.all()]
        return qs.filter(group__in=groups) | public
