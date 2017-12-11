from django.db import models
from django.contrib.auth.models import User
from petpen.settings import MEDIA_ROOT

import os

def get_model_path(instance):
    return os.path.join(MEDIA_ROOT,'models/{}/{}'.format(instance.user,instance.title))

class NN_model(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=30,unique=True)
    state_file = models.FilePathField(path=get_model_path,match='state.json')
    structure_file = models.FilePathField(path=get_model_path,match='result.json')
