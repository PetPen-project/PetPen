from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone as timezone

from petpen.settings import MEDIA_ROOT

import os, shutil
import os.path as op

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
    status_choices = (
        ('idle','system idle'),
        ('loading','loading model structure'),
        ('running','training model'),
        ('editing','editing model structure'),
        ('executing','predicting dataset'),
        ('finish','finish training'),
        ('error','error found'),
    )
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    state_file = models.FilePathField(path=MEDIA_ROOT,match=r'state.json')
    structure_file = models.FilePathField(path=MEDIA_ROOT,match=r'result.json')
    modified = models.DateTimeField(default=timezone.now)
    training_counts = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    status = models.CharField(default='idle',choices=status_choices,max_length=30)

    def delete(self,**kwargs):
        shutil.rmtree(op.join(MEDIA_ROOT,op.dirname(self.structure_file)))
        super().delete(**kwargs)

    def save(self,*args,create=False,**kwargs):
        self.state_file = 'models/{}/{}/state.json'.format(self.user.id,self.title)
        self.structure_file = 'models/{}/{}/result.json'.format(self.user.id,self.title)
        self.modified = timezone.now()
        # create initial files for new project
        if create:
            model_dir = op.dirname(self.structure_file)
            os.makedirs(op.join(MEDIA_ROOT,model_dir))
            shutil.copy2(op.abspath(op.join(op.abspath(__file__),'../../../.config.json')),op.join(MEDIA_ROOT,model_dir))
        super().save(*args,**kwargs)

class History(models.Model):
    project = models.ForeignKey(NN_model,on_delete=models.CASCADE)
    name = models.CharField(max_length=30,blank=True)
    executed = models.DateTimeField(default=timezone.now)
    save_path = models.CharField(max_length=20)
    execution_type = models.CharField(max_length=15,default='training model')
    status = models.CharField(max_length = 30,default='success')

def one_week_period():
    return timezone.now() + timezone.timedelta(days=7)

# class Prediction(models.Model):
    # history = models.ForeignKey(History,on_delete=models.CASCADE)
    # expired = models.DateTimeField(default=one_week_period)
    # created = models.DateTimeField(default=timezone.now)
    # def path(self):
        # return op.join(MEDIA_ROOT,op.dirname(self.history.project.structure_file),self.history.save_path,self.created.strftime('%y%m%d_%H%M%S'))
