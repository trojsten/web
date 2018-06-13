import subprocess
from tempfile import TemporaryFile, NamedTemporaryFile
import zipfile
import os
import constants as const
import re


class DiplomaGenerator:

    def __init__(self, static_path=None):
        self.svg_path = static_path or '.'  # replace with settings.static stuff

    def create_sample(self):
        participants = [{'name': 'Ferko Mrkvička', 'round': '2. Letná časť', 'year': 2018, 'rank': 47}]
        archive = self.create_diplomas(participants=participants, archive=True, separate=True)
        with open("sample.zip", 'wb') as f:
            f.write(archive)

    def create_diplomas(self,
                        template_svg_name='KSP_DIPLOMA',
                        participants=[],
                        archive=False,
                        separate=False):

        template_svg = open(os.path.join(self.svg_path, getattr(const, template_svg_name)), 'r').read()

        f = open(os.path.join(self.svg_path, getattr(const, template_svg_name + '_FIELDS')), 'r')
        template_fields = [line.strip('\n') for line in f.readlines()]

        svgs = self.svgs_for_participants(template_svg,
                                          template_fields,
                                          participants)

        svg_files = [self.make_into_file(svg) for svg in svgs]

        pdfs = self.render_pdfs(svg_files, separate=separate, name_prefix=template_svg_name)

        for f in svg_files:
            f.close()

        if archive:
            return self.create_archive_file(pdfs)
        return pdfs

    def svg_for_participant(self, template_svg, template_fields, participant):
        svg = template_svg
        for attr, value in participant.items():
            pattern = "{%s}" % attr
            if pattern in template_fields:
                svg = re.sub(pattern, str(value), svg)
        return svg

    def svgs_for_participants(self, template_svg, template_fields, participants):
        return [self.svg_for_participant(template_svg, template_fields, participant)
                for participant in participants]

    def render_pdfs(self, svg_files, separate=False, pdf_name='diploma_joined.pdf', name_prefix=""):
        if not isinstance(svg_files, list):
            svg_files = [svg_files]

        command = ['rsvg-convert', '-f', 'pdf']

        if separate:
            return [('%s_%d.pdf' % (name_prefix, num), subprocess.check_output(command, stdin=f))
                    for num, f in enumerate(svg_files)]
        else:
            args = command + [f.name for f in svg_files]
            pdf = subprocess.check_output(args)
            return [(pdf_name, pdf)]

    def make_into_file(self, svg):
        f = NamedTemporaryFile(mode='w')
        f.write(svg)
        f.seek(0)
        return f

    def create_archive_file(self, pdfs):
        if not isinstance(pdfs, list):
            pdfs = [pdfs]

        with TemporaryFile() as tmp:
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as archive:
                for name, content in pdfs:
                    print(name)
                    archive.writestr(name, content)

            tmp.seek(0)
            content = tmp.read()
        return content
