from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone as timezone

from petpen.settings import MEDIA_ROOT

import os

from django.db.models import FilePathField

class DynamicFilePathField(FilePathField):

    def __init__(self, verbose_name=None, name=None, path='', match=None,
                 recursive=False, allow_files=True, allow_folders=False, **kwargs):
        self.path, self.match, self.recursive = path, match, recursive
        if callable(self.path):
            self.pathfunc, self.path = self.path, self.path()
        self.allow_files, self.allow_folders = allow_files, allow_folders
        kwargs['max_length'] = kwargs.get('max_length', 100)
        super(FilePathField, self).__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(FilePathField, self).deconstruct()
        if hasattr(self, "pathfunc"):
            kwargs['path'] = self.pathfunc
        return name, path, args, kwargs

def get_model_path(instance):
    return os.path.join(MEDIA_ROOT,'models/{}/{}'.format(instance.user.id,instance.title))

class NN_model(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    state_file = models.FilePathField(path=MEDIA_ROOT,match=r'state.json')
    structure_file = models.FilePathField(path=MEDIA_ROOT,match=r'result.json')
    modified = models.DateTimeField(default=timezone.now)
    training_counts = models.IntegerField(default=0)
    status = models.CharField(default='idle',max_length=30)

class History(models.Model):
    project = models.ForeignKey(NN_model,on_delete=models.CASCADE)
    name = models.CharField(max_length=30,blank=True)
    executed = models.DateTimeField(default=timezone.now)
    save_path = models.CharField(max_length=20)
    execution_type = models.CharField(max_length=15,default='training model')
    status = models.CharField(max_length = 30,default='success')
