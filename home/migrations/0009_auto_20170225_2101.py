# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-25 21:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_plan_is_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plan',
            old_name='price_per_month',
            new_name='price',
        ),
        migrations.AddField(
            model_name='plan',
            name='currency',
            field=models.CharField(choices=[(b'USD', b'USD'), (b'INR', b'INR')], default='USD', max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plan',
            name='identifier',
            field=models.CharField(default='xxx', max_length=20),
        ),
        migrations.AddField(
            model_name='plan',
            name='interval',
            field=models.CharField(choices=[('month', 'month'), ('year', 'year')], default='month', max_length=20),
            preserve_default=False,
        ),
    ]
