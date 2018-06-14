import zipfile
import os

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from sendfile import sendfile

from trojsten.diplomas.api import DiplomaGenerator
from trojsten.diplomas.helpers import parse_participants
from trojsten.diplomas.forms import DiplomaParametersForm


@login_required
def view_diplomas(request):
    if request.method == 'POST':
        form = DiplomaParametersForm(request.POST, request.FILES)
        if form.is_valid():
            pfile = form.cleaned_data['participant_file']
            participant_data, error_msg = parse_participants(pfile)
            if not participant_data:
                messages.add_message(request, messages.ERROR, error_msg)
            else:

                separate = not form.cleaned_data['join_pdf']
                template_name = form.cleaned_data['template']

                generator = DiplomaGenerator()
                pdfs = generator.create_diplomas(participant_data, template_svg_name=template_name, separate=separate)
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
        form = DiplomaParametersForm()

    context = {
        'form': form
    }

    return render(
        request, 'trojsten/diplomas/view_diplomas.html', context
    )