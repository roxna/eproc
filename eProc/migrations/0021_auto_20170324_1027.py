# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-24 10:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0020_drawdownitem_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='drawdownitem',
            name='location',
        ),
        migrations.AddField(
            model_name='buyerco',
            name='subscription',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='buyer_co', to='eProc.Subscription'),
        ),
    ]
