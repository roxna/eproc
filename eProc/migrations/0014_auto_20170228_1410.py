# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-28 14:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0013_pricealert'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pricealert',
            old_name='price',
            new_name='alert_price',
        ),
        migrations.RemoveField(
            model_name='pricealert',
            name='currency',
        ),
        migrations.AlterField(
            model_name='pricealert',
            name='commodity',
            field=models.CharField(choices=[(b'Steel', b'Steel'), (b'Iron Ore', b'Iron Ore')], max_length=100),
        ),
    ]
