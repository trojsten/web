from django.views.generic import ListView
from django.contrib.sites.models import get_current_site

from trojsten.news.models import Entry


class EntryListView(ListView):
    model = Entry
    template_name = 'trojsten/news/index.html'
    context_object_name = 'news_entries'
    paginate_by = 10

    def get_queryset(self):
        return self.model.objects.filter(
            sites__id__exact=get_current_site(self.request).id)
