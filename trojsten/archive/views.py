from django.shortcuts import render

from wiki.decorators import get_article

from trojsten.regal.contests.models import Competition

@get_article(can_read=True)
def archive(request, article, *args, **kwargs):
    competitions = Competition.objects.all()  # Todo: filter by site
    kwargs.update({
        'article': article,
        'competitions': competitions,
    })
    return render(request, 'trojsten/archive/archive.html', kwargs)
