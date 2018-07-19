# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import subprocess
from tempfile import NamedTemporaryFile
import re

from django.utils import timezone

from .constants import FIELD_REPLACE_PATTERN


class DiplomaGenerator:
    """
    Provides necessary methods for handling SVG files and templating them into diplomas
    """

    def create_diplomas(self,
                        participants,
                        template_svg,
                        join=False):
        """

        :param participants: A list of dict objects, where keys are fields to replace and values are values
        :param template_svg: string content of SVG file
        :param separate: boolean whether resulting PDFs are to be joined together or not
        :return: PDF(s) containing generated diplomas
        """

        svgs = [self.svg_for_participant(template_svg, participant)
                for participant in participants]

        pdfs = self.render_pdfs(svgs,
                                join=join,
                                name_prefix=timezone.localtime().strftime("%Y-%m-%d-%H-%M"))

        return pdfs

    def svg_for_participant(self, template_svg, participant):
        svg = template_svg
        for attr, value in participant.items():
            pattern = FIELD_REPLACE_PATTERN.format(attr)
            svg = re.sub(pattern, str(value), svg)
        return svg

    def render_pdfs(self, svgs, join=False, name_prefix=""):

        def make_into_file(content):
            tmp = NamedTemporaryFile(mode='w')
            tmp.write(content)
            tmp.seek(0)
            return tmp

        if not isinstance(svgs, list):
            svgs = [svgs]

        svg_files = [make_into_file(svg) for svg in svgs]

        command = ['rsvg-convert', '-f', 'pdf']

        if join:
            args = command + [f.name for f in svg_files]
            pdf = subprocess.check_output(args)
            pdfs = [('diplomas_joined.pdf', pdf)]

        else:
            pdfs = [('%s_%d.pdf' % (name_prefix, num), subprocess.check_output(command, stdin=f))
                    for num, f in enumerate(svg_files)]

        for f in svg_files:
            f.close()

        return pdfs

    @staticmethod
    def render_png(svg):
        f = NamedTemporaryFile(mode='w')
        f.write(svg)
        f.seek(0)
        png = subprocess.check_output(['rsvg-convert', '-f', 'png', f.name])
        f.close()
        return png
