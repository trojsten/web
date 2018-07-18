# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import zipfile
import json
from tempfile import TemporaryFile

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from trojsten.diplomas.generator import DiplomaGenerator
from trojsten.diplomas.forms import DiplomaParametersForm
from trojsten.diplomas.models import DiplomaTemplate

from wiki.decorators import get_article
from .sources import SOURCE_CLASSES


@csrf_exempt
@login_required
def source_request(request, source_class):
    source_instance = SOURCE_CLASSES[source_class]()
    user_data = source_instance.handle_request(request)
    return JsonResponse(user_data, safe=False)


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
    return render(request, 'trojsten/diplomas/sources.html', {'sources': sources})


@login_required
def diploma_preview(request, diploma_id):
    diploma = DiplomaTemplate.objects.get(pk=diploma_id)
    if diploma:
        png = DiplomaGenerator.render_png(diploma.svg)
        return HttpResponse(png, content_type="image/png")
    else:
        return HttpResponseNotFound()


@get_article
@login_required
def view_diplomas(request, article, *args, **kwargs):

    user_groups = request.user.groups.all()

    diploma_templates = DiplomaTemplate.objects.filter(authorized_groups__in=user_groups).order_by('name').distinct()

    if request.user.is_superuser:
        diploma_templates = DiplomaTemplate.objects.get_queryset()

    if request.method == 'POST':
        form = DiplomaParametersForm(diploma_templates, request.POST, request.FILES)
        if form.is_valid():

            template_pk = form.cleaned_data['template']
            participants_data = form.cleaned_data['participants_data']
            separate = not form.cleaned_data['join_pdf']

            template = diploma_templates.filter(pk=template_pk).get()

            if template:
                svg = template.svg

                generator = DiplomaGenerator()
                pdfs = generator.create_diplomas(participants_data, template_svg=svg, separate=separate)

                archive_file = TemporaryFile(mode='w+b')
                with zipfile.ZipFile(archive_file, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for name, content in pdfs:
                        archive.writestr(name, content)
                archive_file.seek(0)

                filename = timezone.localtime().strftime(
                    "diplom_{}_%Y_%m_%d_%H:%M:%S.zip".format(request.user.last_name))

                response = HttpResponse()
                response['Content-type'] = 'application/zip'
                response['Content-Description'] = 'File Transfer'
                response['Content-Disposition'] = 'attachment; filename="%s"' % filename
                response['Content-Transfer-Encoding'] = 'binary'

                response.write(archive_file.read())

                archive_file.close()

                return response
            else:
                messages.add_message(request, messages.ERROR,
                                     _("Trying to access non-existent or restricted template"))
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
        'article': article,
        'template_fields': json.dumps(editable_fields, ensure_ascii=False).encode('utf8')
    }

    return render(
        request, 'trojsten/diplomas/view_diplomas.html', context
    )
