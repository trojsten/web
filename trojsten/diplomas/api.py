# -*- coding: utf-8 -*-

import subprocess
from datetime import datetime
from tempfile import TemporaryFile, NamedTemporaryFile
import zipfile
import os
import re

from .constants import FIELD_REPLACE_PATTERN


class DiplomaGenerator:

    def __init__(self, static_path=None):
        self.svg_path = static_path or os.path.join(os.path.dirname(__file__), 'static/diplomas/')

    def create_sample(self):
        participants = [{'name': 'Ferko Mrkvička', 'round': '2. Letná časť', 'year': 2018, 'rank': 47}]
        return self.create_diplomas(participants, separate=True)[0]

    def create_diplomas(self,
                        participants,
                        template_svg,
                        separate=False):

        svgs = [self.svg_for_participant(template_svg, participant)
                for participant in participants]

        pdfs = self.render_pdfs(svgs,
                                separate=separate,
                                name_prefix=datetime.now().strftime("%Y-%m-%d-%H-%M"))

        return pdfs

    def svg_for_participant(self, template_svg, participant):
        svg = template_svg
        for attr, value in participant.items():
            pattern = FIELD_REPLACE_PATTERN.format(attr)
            svg = re.sub(pattern, str(value), svg)
        return svg

    def render_pdfs(self, svgs, separate=False, pdf_name='diploma_joined.pdf', name_prefix=""):

        def make_into_file(content):
            tmp = NamedTemporaryFile(mode='w')
            tmp.write(content)
            tmp.seek(0)
            return tmp

        if not isinstance(svgs, list):
            svgs = [svgs]

        svg_files = [make_into_file(svg) for svg in svgs]

        command = ['rsvg-convert', '-f', 'pdf']

        if separate:
            pdfs = [('%s_%d.pdf' % (name_prefix, num), subprocess.check_output(command, stdin=f))
                    for num, f in enumerate(svg_files)]
        else:
            args = command + [f.name for f in svg_files]
            pdf = subprocess.check_output(args)
            pdfs = [(pdf_name, pdf)]

        for f in svg_files:
            f.close()

        return pdfs

    def create_archive_file(self, pdfs):
        if not isinstance(pdfs, list):
            pdfs = [pdfs]

        with TemporaryFile() as tmp:
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as archive:
                for name, content in pdfs:
                    archive.writestr(name, content)

            tmp.seek(0)
            content = tmp.read()
        return content
