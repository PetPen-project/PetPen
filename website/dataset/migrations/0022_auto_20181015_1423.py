# Generated by Django 2.0.3 on 2018-10-15 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0021_dataset_has_labels'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='feature_labels',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='target_labels',
        ),
    ]
