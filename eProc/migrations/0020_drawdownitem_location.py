# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-23 13:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0019_auto_20170321_0747'),
    ]

    operations = [
        migrations.AddField(
            model_name='drawdownitem',
            name='location',
            field=models.ForeignKey(default=22, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='eProc.Location'),
            preserve_default=False,
        ),
    ]
