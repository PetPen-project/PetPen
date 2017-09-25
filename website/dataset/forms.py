from django import forms

from .formatChecker import ExtFileField

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    training_csvfile = ExtFileField(
        label='select a csv file',
        help_text='training data',
        content_types=['.csv'],
    )
    testing_csvfile = ExtFileField(
        label='select a csv file',
        help_text='testing data',
        content_types=['.csv'],
    )
    is_image = forms.BooleanField()
    shared_testing = forms.BooleanField()
    
