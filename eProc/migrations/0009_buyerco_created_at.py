# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-25 22:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0008_auto_20170225_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyerco',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
