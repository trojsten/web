from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.contrib.sites.models import get_current_site

from .models import Thread


class ThreadView(DetailView):
    template_name = "trojsten/threads/thread.html"
    model = Thread
    context_object_name = 'thread'
    pk_url_kwarg = 'thread_id'


class ThreadListView(ListView):
    template_name = 'trojsten/threads/index.html'
    model = Thread
    context_object_name = 'threads'

    def get_queryset(self):
        return self.model.objects.filter(
            sites__id__exact=get_current_site(self.request).id)
