# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-08 03:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0036_auto_20170105_1505'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rating',
            old_name='value',
            new_name='score',
        ),
        migrations.AddField(
            model_name='rating',
            name='category',
            field=models.CharField(choices=[('Quality', 'Quality'), ('Delivery', 'Delivery'), ('Cost', 'Cost'), ('Responsiveness', 'Responsiveness'), ('Total', 'Total')], default='Total', max_length=15),
        ),
    ]
