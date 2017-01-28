# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-28 06:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='drawdown',
            name='department',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='drawdowns', to='eProc.Department'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='document',
            name='sub_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='location',
            name='address2',
            field=models.CharField(default='-', max_length=40),
        ),
        migrations.AlterField(
            model_name='location',
            name='loc_type',
            field=models.CharField(choices=[(b'Billing', b'Billing'), (b'Shipping', b'Shipping'), (b'HQ', b'HQ')], default='HQ', max_length=20),
        ),
    ]
