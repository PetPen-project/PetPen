from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User

import os, re, datetime

def training_dataset_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<user_id>/<dataset_name>/<filename>
    return 'datasets/{0}/{1}/{2}'.format(instance.user.id, instance.title, 'train.csv')

def testing_dataset_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<user_id>/<dataset_name>/<filename>
    return 'datasets/{0}/{1}/{2}'.format(instance.user.id, instance.title, 'test.csv')

def dataset_path(instance, filename):
    return 'datasets/{0}/{1}/{2}'.format(instance.user.id, instance.title, filename)

FILE_CHOICES = (
    ('CSV','csv'),
    ('PKL','pickle'),
    ('NPY','npy'),
    ('IMG','images'),
)

class Dataset(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE) 
    training_input_file = models.FileField(upload_to=dataset_path)
    testing_input_file = models.FileField(upload_to=dataset_path)
    training_output_file = models.FileField(upload_to=dataset_path)
    testing_output_file = models.FileField(upload_to=dataset_path)
    title = models.CharField(max_length=50)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    train_input_size = models.IntegerField(default=0)
    test_input_size = models.IntegerField(default=0)
    train_output_size = models.IntegerField(default=0)
    test_output_size = models.IntegerField(default=0)
    train_samples = models.IntegerField(default=0)
    test_samples = models.IntegerField(default=0)
    input_shape = models.CharField(max_length=100)
    output_shape = models.CharField(max_length=100)
    description = models.TextField(default='')
    filetype = models.CharField(max_length=3, choices=FILE_CHOICES, default='CSV')
    is_image = models.BooleanField(default=False)
    feature_labels = models.TextField(default="")
    target_labels = models.TextField(default="")
