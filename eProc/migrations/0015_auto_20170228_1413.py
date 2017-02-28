# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-28 14:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0014_auto_20170228_1410'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[(b'Steel', b'Steel'), (b'Iron Ore', b'Iron Ore')], max_length=100)),
                ('api_key_code', models.CharField(max_length=20)),
                ('unit', models.CharField(default='$/mt', max_length=10)),
            ],
        ),
        migrations.AlterField(
            model_name='pricealert',
            name='commodity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_alerts', to='eProc.Commodity'),
        ),
    ]
