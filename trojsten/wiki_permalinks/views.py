from django.shortcuts import redirect, get_object_or_404
from wiki.models.article import Article

def transform_wiki_link(request, article_id):
    return redirect(get_object_or_404(Article, pk=article_id).get_absolute_url())
