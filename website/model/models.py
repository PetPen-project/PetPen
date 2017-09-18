from django.db import models
# from django.utils import timezone
from .formatChecker import ContentTypeRestrictedFileField

class Document(models.Model):
    # docfile = ContentTypeRestrictedFileField(upload_to='data', content_types=['text/csv'], max_upload_size=5242880)
    docfile = models.FileField(upload_to='data')


# class Post(models.Model):
    # author = models.ForeignKey(User)
    # title = models.CharField(max_length=200)
    # text = models.TextField()
    # created_date = models.DateTimeField(
            # default=timezone.now)
    # published_date = models.DateTimeField(
            # blank=True, null=True)

    # def publish(self):
        # self.published_date = timezone.now()
        # self.save()

    # def __str__(self):
        # return self.title

