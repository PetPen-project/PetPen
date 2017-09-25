from django.db import models
from django.dispatch import receiver

import os

def training_dataset_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/{1}'.format(instance.title, 'train.csv')
def testing_dataset_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/{1}'.format(instance.title, 'test.csv')

class Dataset(models.Model):
    training_csvfile = models.FileField(upload_to=training_dataset_path)
    testing_csvfile = models.FileField(upload_to=testing_dataset_path)
    title = models.CharField(max_length=50)
    is_image = models.BooleanField(default=False)
    shared_testing = models.BooleanField(default=False)

@receiver(models.signals.post_delete, sender=Dataset)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.training_csvfile:
        if os.path.isfile(instance.training_csvfile.path):
            os.remove(instance.training_csvfile.path)
    if instance.testing_csvfile:
        if os.path.isfile(instance.testing_csvfile.path):
            os.remove(instance.testing_csvfile.path)

@receiver(models.signals.pre_save, sender=Dataset)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Dataset.objects.get(pk=instance.pk).training_csvfile
    except Dataset.DoesNotExist:
        return False

    new_file = instance.training_csvfile
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
    try:
        old_file = Dataset.objects.get(pk=instance.pk).testing_csvfile
    except Dataset.DoesNotExist:
        return False

    new_file = instance.testing_csvfile
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
