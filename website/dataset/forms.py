from django import forms

from .formatChecker import ExtFileField

content_types = ['.csv','.pickle','.pkl','.npy']
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    training_input_file = ExtFileField(
        help_text='select a csv/pickle file',
        label='training input data',
        content_types=content_types,
    )
    testing_input_file = ExtFileField(
        help_text='select a csv/pickle file',
        label='testing input data',
        content_types=content_types,
    )
    training_output_file = ExtFileField(
        help_text='select a csv/pickle file',
        label='training output data',
        content_types=content_types,
    )
    testing_output_file = ExtFileField(
        help_text='select a csv/pickle file',
        label='testing output data',
        content_types=content_types,
    )
    # is_image = forms.BooleanField(required=False)
    
