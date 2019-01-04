# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-29 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0007_auto_20180117_2014'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='filetype',
            field=models.CharField(choices=[('CSV', 'csv'), ('PKL', 'pickle')], default=('CSV', 'csv'), max_length=3),
        ),
        migrations.AddField(
            model_name='dataset',
            name='test_input_size',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dataset',
            name='test_output_size',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dataset',
            name='test_samples',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dataset',
            name='train_input_size',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dataset',
            name='train_output_size',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dataset',
            name='train_samples',
            field=models.IntegerField(default=0),
        ),
    ]
