# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-13 21:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0002_auto_20171113_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nn_model',
            name='title',
            field=models.CharField(max_length=30),
        ),
    ]
