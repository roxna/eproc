# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-04 20:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0004_category_buyerco'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='buyerCo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='eProc.BuyerCo'),
        ),
    ]
