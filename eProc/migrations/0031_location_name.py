# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-14 23:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0030_buyerprofile_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='name',
            field=models.CharField(default='location name', max_length=50),
            preserve_default=False,
        ),
    ]
