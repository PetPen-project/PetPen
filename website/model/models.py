from django.db import models
# from django.utils import timezone
from .formatChecker import ContentTypeRestrictedFileField

class Document(models.Model):
    # docfile = ContentTypeRestrictedFileField(upload_to='data', content_types=['text/csv'], max_upload_size=5242880)
    docfile = models.FileField(upload_to='data')

