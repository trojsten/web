from __future__ import unicode_literals

import json

from django import forms
from django.conf import settings

default_config = getattr(settings, "EDITOR_CONFIG", {})
script_url = "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.39.0"


class Editor(forms.Textarea):
    """
    A widget designed to replace a standard TextArea element with a JS component provided
    by CodeMirror. Highly customizable, see https://codemirror.net/ for reference.
    """

    def __init__(self, **kwargs):
        self.config = default_config
        self.config.update(kwargs)
        super(Editor, self).__init__()

    @property
    def media(self):
        css = ("%s/codemirror.css" % script_url,)
        if "theme" in self.config:
            css = css + ("%s/theme/%s.css" % (script_url, self.config["theme"]),)

        js = ("%s/codemirror.js" % script_url,)
        if "mode" in self.config:
            if isinstance(self.config["mode"], dict) and "name" in self.config["mode"]:
                mode = self.config["mode"]["name"]
            else:
                mode = self.config["mode"]
            js = js + ("%s/mode/%s/%s.js" % (script_url, mode, mode),)

        return forms.Media(css={"all": css}, js=js)

    def render(self, name, value, attrs=None, **kwargs):
        field = super(Editor, self).render(name, value, attrs)
        return (
            "%s<script>"
            'var editor = CodeMirror.fromTextArea(document.getElementById("%s"), %s);'
            "</script>"
        ) % (field, attrs["id"], json.dumps(self.config))
