# Generated by Django 2.0.3 on 2018-05-20 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0013_auto_20180520_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nn_model',
            name='status',
            field=models.CharField(choices=[('idle', 'system idle'), ('loading', 'loading model structure'), ('running', 'training model'), ('editing', 'editing model structure'), ('executing', 'predicting dataset'), ('finish', 'finish training'), ('error', 'error found')], default='idle', max_length=30),
        ),
    ]
