from django import forms
from django.conf import settings


class SourceSubmitForm(forms.Form):
    LANGUAGE_CHOICES = (
        (".", "Zisti podla pripony"),
        (".cc", "C++ (.cpp/.cc)"),
        (".pas", "Pascal (.pas/.dpr)"),
        (".c", "C (.c)"),
        (".py", "Python 3.2 (.py/.py3)"),
        (".hs", "Haskell (.hs)"),
        (".cs", "C# (.cs)"),
        (".java", "Java (.java)")
    )
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH)
    language = forms.ChoiceField(label='Jazyk',
                                 choices=LANGUAGE_CHOICES)

    def __init__(self, *args, **kwargs):
        task_language = ""

        super(SourceSubmitForm, self).__init__(*args, **kwargs)

        if "task_language" in kwargs:
            task_language = kwargs["task_language"]
            del kwargs["task_language"]

        if task_language != "":
            choices_dict = {x[0]: x[1] for x in self.LANGUAGE_CHOICES}
            choices = (
                ("." + task_language, choices_dict["." + task_language]),)

            self.fields['language'].choices = choices


class DescriptionSubmitForm(forms.Form):
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH)

    def __init__(self, *args, **kwargs):
        super(DescriptionSubmitForm, self).__init__(*args, **kwargs)
