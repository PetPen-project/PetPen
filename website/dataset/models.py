from django.db import models
from django.dispatch import receiver

import os

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/{1}'.format(instance.title, 'train.csv')

class Dataset(models.Model):
    csvfile = models.FileField(upload_to=user_directory_path)
    title = models.CharField(max_length=50)

@receiver(models.signals.post_delete, sender=Dataset)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.csvfile:
        if os.path.isfile(instance.csvfile.path):
            os.remove(instance.csvfile.path)

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
        old_file = Dataset.objects.get(pk=instance.pk).csvfile
    except Dataset.DoesNotExist:
        return False

    new_file = instance.csvfile
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
