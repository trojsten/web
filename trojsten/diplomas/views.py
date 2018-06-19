# -*- coding: utf-8 -*-
import zipfile
import os
import json

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from sendfile import sendfile

from trojsten.diplomas.api import DiplomaGenerator
from trojsten.diplomas.forms import DiplomaParametersForm
from trojsten.diplomas.models import DiplomaTemplate

from wiki.decorators import get_article


@get_article
@login_required
def view_diplomas(request, article, *args, **kwargs):
    diploma_templates = DiplomaTemplate.objects.get_queryset()
    editable_fields = {}
    for d in diploma_templates:
        editable_fields[d.pk] = d.editable_fields

    if request.method == 'POST':
        form = DiplomaParametersForm(diploma_templates, request.POST, request.FILES)
        if form.is_valid():

            participants_data = form.cleaned_data['participants_data']
            print(participants_data)
            separate = not form.cleaned_data['join_pdf']
            template_pk = form.cleaned_data['template']
            svg = diploma_templates.filter(pk=template_pk).get().svg

            generator = DiplomaGenerator()
            pdfs = generator.create_diplomas(participants_data, template_svg=svg, separate=separate)
            path = os.path.join(os.path.dirname(__file__), 'archive.zip')
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
                for name, content in pdfs:
                    archive.writestr(name, content)
            return sendfile(request, path, attachment=True)

        else:
            for field in form:
                for error in field.errors:
                    messages.add_message(request, messages.ERROR,
                                         '%s: %s' % (field.label, error))
    else:
        form = DiplomaParametersForm(diploma_templates)

    context = {
        'form': form,
        'article': article,
        'template_fields': json.dumps(editable_fields, ensure_ascii=False).encode('utf8')
    }

    return render(
        request, 'trojsten/diplomas/test_template.html', context
    )
