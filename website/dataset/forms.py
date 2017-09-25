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
        required = False
    )
    is_image = forms.BooleanField(required=False)
    shared_testing = forms.BooleanField(required=False, help_text='use the same csv for testing')
    
