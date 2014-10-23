from django import forms

class ReviewForm (forms.Form):
    file = forms.FileField(max_length=128)
    user = forms.ChoiceField ()
    points = forms.IntegerField(min_value=0, required=False)

    def __init__ (self, *args, **kwargs):
        choices = kwargs.pop("choices")
        max_value = kwargs.pop("max_value")
        super(ReviewForm, self).__init__(*args, **kwargs)

        self.fields["user"].choices = choices
        self.fields["points"] = forms.IntegerField(min_value=0, max_value=max_value, required=False)

