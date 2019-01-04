from django import forms

from .formatChecker import ExtFileField

content_types = ['.csv','.pickle','.pkl','.npy','.zip']
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    # training_input_img = ExtFileField(
        # help_text='(in zip format)',
        # label='training input images',
        # content_types=['.zip'],
    # )
    # testing_input_img = ExtFileField(
        # help_text='(in zip format)',
        # label='testing input images',
        # content_types=['.zip'],
    # )
    # training_output_img = ExtFileField(
        # help_text='(in zip format)',
        # label='training output images',
        # content_types=['.zip'],
    # )
    # testing_output_img = ExtFileField(
        # help_text='(in zip format)',
        # label='testing output images',
        # content_types=['.zip'],
    # )
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
    feature_labels = forms.CharField(label='feature labels',required=False,widget=forms.TextInput(attrs={'size': '60'}))
    target_labels = forms.CharField(label='target labels',required=False,widget=forms.TextInput(attrs={'size': '60'}))
    # is_image = forms.BooleanField(required=False)
    
