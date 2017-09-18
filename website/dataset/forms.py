from django import forms

from .formatChecker import ExtFileField

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    csvfile = ExtFileField(
        label='select a csv file',
        help_text='training data',
        content_types=['.csv'],
    )
