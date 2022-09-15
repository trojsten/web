# -*- coding: utf-8 -*-
import re
import subprocess
from tempfile import NamedTemporaryFile

from django.utils import timezone

from .constants import DIPLOMA_DEFAULT_NAME, FIELD_REPLACE_PATTERN


class DiplomaGenerator:
    """
    Provides necessary methods for handling SVG files and templating them into diplomas.
    """

    def create_diplomas(self, participants, template_svg, join=False):
        """
        Given a list of participants and a template SVG creates a PDF diploma for every participant
        from the template.

        :param participants: A list of dict objects, where keys are fields to replace and values
                             are the values.
        :param template_svg: string content of SVG file.
        :param join: boolean whether resulting PDFs are to be joined together or not.
        :return: PDF(s) containing generated diplomas.
        """

        svgs = [self.svg_for_participant(template_svg, participant) for participant in participants]

        pdfs = self.render_pdfs(
            svgs, join=join, name_prefix=timezone.localtime().strftime("%Y-%m-%d-%H-%M")
        )

        return pdfs

    def svg_for_participant(self, template_svg, participant):
        svg = template_svg
        for attr, value in participant.items():
            try:
                if not isinstance(value, unicode):
                    value = str(value)
            except NameError:
                if not isinstance(value, str):
                    value = str(value)
            pattern = FIELD_REPLACE_PATTERN.format(field_name=attr)
            svg = re.sub(pattern, value, svg)
        return svg

    @staticmethod
    def make_into_file(content):
        tmp = NamedTemporaryFile(mode="wb")
        tmp.write(content.encode("utf-8"))
        tmp.seek(0)
        return tmp

    def render_pdfs(self, svgs, join=False, name_prefix=""):
        if not isinstance(svgs, list):
            svgs = [svgs]

        svg_files = [self.make_into_file(svg) for svg in svgs]

        command = ["rsvg-convert", "-f", "pdf"]
        try:
            if join:
                args = command + [f.name for f in svg_files]
                pdf = subprocess.check_output(args)
                pdfs = [(DIPLOMA_DEFAULT_NAME, pdf)]

            else:
                pdfs = [
                    ("%s_%d.pdf" % (name_prefix, num), subprocess.check_output(command, stdin=f))
                    for num, f in enumerate(svg_files)
                ]
        finally:
            for f in svg_files:
                f.close()

        return pdfs

    @staticmethod
    def render_png(svg):
        f = DiplomaGenerator.make_into_file(svg)
        try:
            png = subprocess.check_output(["rsvg-convert", "-f", "png", f.name])
        finally:
            f.close()
        return png
