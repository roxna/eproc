# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-25 05:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0006_auto_20170225_0430'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='current_status',
            field=models.CharField(choices=[(b'Pending', b'Pending'), (b'Approved', b'Approved'), (b'Denied', b'Denied'), (b'Cancelled', b'Cancelled'), (b'Open', b'Open'), (b'Closed', b'Closed')], default='Pending', max_length=25),
        ),
    ]