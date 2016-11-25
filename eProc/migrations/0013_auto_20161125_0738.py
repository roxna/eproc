# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-25 07:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0012_auto_20161125_0252'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountcode',
            name='description',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='is_approved',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('Requested', 'Requested'), ('Approved', 'Approved'), ('Ordered', 'Ordered'), ('Delivered', 'Delivered')], default='Pending', max_length=20),
        ),
    ]
