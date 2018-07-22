# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import zipfile
import json
from functools import wraps
from tempfile import TemporaryFile

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from trojsten.diplomas.generator import DiplomaGenerator
from trojsten.diplomas.forms import DiplomaParametersForm
from trojsten.diplomas.models import DiplomaTemplate

from wiki.decorators import get_article
from .sources import SOURCE_CLASSES


def access_filter(f):
    @wraps(f)
    def wrapper(request, diploma_id, *args, **kwargs):
        template = DiplomaTemplate.objects.filter(pk=diploma_id)
        if not template:
            return HttpResponseNotFound(_('Template does not exist'))

        if request.user.is_superuser:
            return f(request, diploma_id, *args, **kwargs)

        user_groups = request.user.groups.all()
        intersect = template.filter(authorized_groups__in=user_groups).distinct()
        if not intersect:
            return HttpResponseForbidden(_('You do not have access to this template'))

        return f(request, diploma_id, *args, **kwargs)
    return wrapper


@get_article
@login_required
def view_tutorial(request, article, *args, **kwargs):
    return render(request, 'trojsten/diplomas/parts/tutorial.html', {'article': article})


@login_required
def source_request(request, source_class):
    source_instance = SOURCE_CLASSES[source_class]()
    user_data = source_instance.handle_request(request)
    return JsonResponse(user_data, safe=False)


@access_filter
@login_required
def diploma_sources(request, diploma_id):
    diploma = DiplomaTemplate.objects.get(pk=diploma_id)
    sources = []
    for source in diploma.sources.all():
        src = source.source_class()
        sources.append({'html': src.render(),
                        'name': src.name,
                        'verbose_name': source.name
                        })
    return render(request, 'trojsten/diplomas/parts/sources.html', {'sources': sources})


@access_filter
@login_required
def diploma_preview(request, diploma_id):
    diploma = DiplomaTemplate.objects.get(pk=diploma_id)
    if diploma:
        png = DiplomaGenerator.render_png(diploma.svg)
        return HttpResponse(png, content_type='image/png')
    return HttpResponseNotFound()


@login_required
def view_diplomas(request):

    user_groups = request.user.groups.all()

    diploma_templates = DiplomaTemplate.objects.get_queryset().order_by('name')

    if not request.user.is_superuser:
        diploma_templates = diploma_templates.filter(authorized_groups__in=user_groups).distinct()

    if not diploma_templates.exists():
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = DiplomaParametersForm(diploma_templates, data=request.POST, files=request.FILES)
        if form.is_valid():

            template_pk = form.cleaned_data['template']
            participants_data = form.cleaned_data['participants_data']
            join = form.cleaned_data['join_pdf']

            template = diploma_templates.filter(pk=template_pk).get()

            if template:
                svg = template.svg

                generator = DiplomaGenerator()
                pdfs = generator.create_diplomas(participants_data, template_svg=svg, join=join)

                archive_file = TemporaryFile(mode='w+b')
                with zipfile.ZipFile(archive_file, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for name, content in pdfs:
                        archive.writestr(name, content)
                archive_file.seek(0)

                filename = timezone.localtime().strftime(
                    'diplom_{}_%Y_%m_%d_%H:%M:%S.zip'.format(request.user.last_name))

                response = HttpResponse(content_type='application/zip')
                response['Content-Description'] = 'File Transfer'
                response['Content-Disposition'] = 'attachment; filename=\'%s\'' % filename
                response['Content-Transfer-Encoding'] = 'binary'

                response.write(archive_file.read())

                archive_file.close()

                return response
        else:
            for field in form:
                for error in field.errors:
                    messages.add_message(request, messages.ERROR,
                                         '%s: %s' % (field.label, error))
    else:
        form = DiplomaParametersForm(diploma_templates)

    editable_fields = {}
    for d in diploma_templates:
        editable_fields[d.pk] = sorted(d.editable_fields)

    context = {
        'form': form,
        'template_fields': json.dumps(editable_fields, ensure_ascii=False).encode('utf8')
    }

    return render(
        request, 'trojsten/diplomas/view_diplomas.html', context
    )
