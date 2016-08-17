#Indexes for haystack elasticsearch
from django.conf import settings

from haystack import indexes
from wiki.models import Article


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    #modified = indexes.DateField(model_attr='modified')
    #title = indexes.CharField(model_attr='current_revision.title')
    #content = indexes.CharField(model_attr='current_revision.content')

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(urlpath__site_id=settings.SITE_ID)
