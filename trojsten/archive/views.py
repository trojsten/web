from django.shortcuts import render
from wiki.decorators import get_article


@get_article(can_read=True)
def archive(request, article, *args, **kwargs):
    kwargs.update({
        'article': article,
    })
    return render(request, 'trojsten/archive/archive.html', kwargs)
