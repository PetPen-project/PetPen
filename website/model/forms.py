from django import forms

from .formatChecker import ExtFileField
from dataset.models import Dataset
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    # docfile = forms.FileField(
    docfile = ExtFileField(
        label='select a csv file',
        help_text='training data file',
        content_types=['text/csv'],
    )

class DatasetForm(forms.Form):
    dataset_choices = [('test','test')]+[(dataset.title, dataset.title) for dataset in Dataset.objects.all()]
    dataset = forms.ChoiceField(choices=dataset_choices, widget=forms.Select(attrs={'id':'select_dataset','name':'sel_data','onchange':'this.form.submit();'}))

class FeatureForm(forms.Form):
    input_features = forms.MultipleChoiceField()
    output_features = forms.MultipleChoiceField()
    def __init__(self, *args, **kwargs):
        self.feature_choices = kwargs.pop('features')
        super().__init__(*args, **kwargs)
        self.fields['input_features'].choice = self.feature_choices
        self.fields['output_features'].choice = self.feature_choices
# input_features = forms.MultipleChoiceField(widget=forms.SelectMultiple())
    # output_features = forms.MultipleChoiceField(choices=feature_choices)
