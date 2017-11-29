from django.forms import ModelForm, Form
from django import forms
from model.models import NN_model
from petpen.settings import MEDIA_ROOT

class NN_modelForm(forms.Form):
    title = forms.CharField(max_length=30,label='Project title')
    # state_file = forms.FilePathField(path=MEDIA_ROOT,match=r'state.json',recursive=True)

# class NN_modelForm(ModelForm):
    # class Meta:
        # model = NN_model
        # fields = ['user','title','modified','training_counts']
