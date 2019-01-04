from django.forms import ModelForm, Form
from django import forms
from model.models import NN_model
from petpen.settings import MEDIA_ROOT

class NN_modelForm(forms.Form):
    title = forms.CharField(max_length=30,label='Project title')
    # state_file = forms.FilePathField(path=MEDIA_ROOT,match=r'state.json',recursive=True)

# class NN_modelForm_test(ModelForm):
    # class Meta:
        # model = NN_model
        # fields = ['user','title','status','training_counts']

    # def is_valid(self):
        # valid = super().is_valid()
        # # if not valid:
            # # return valid
        # try:
            # instance_id = self.instance.pk
            # #check duplicate title
            # NN_model.objects.filter(user=)
            # if instance_id:
                # pass
            # projects = self.model.
        # return False
