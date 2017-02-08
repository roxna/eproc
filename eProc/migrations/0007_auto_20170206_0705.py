# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-06 07:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0006_auto_20170204_2344'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='buyer_co',
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='description',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/catalog/bulk'),
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='item_type',
            field=models.CharField(choices=[('Vendor Uploaded', 'Vendor Uploaded'), ('Bulk Discount', 'Bulk Discount')], default='Vendor Uploaded', max_length=20),
        ),
        migrations.AlterField(
            model_name='catalogitem',
            name='buyer_co',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='catalog_items', to='eProc.BuyerCo'),
        ),
        migrations.AlterField(
            model_name='rating',
            name='category',
            field=models.CharField(choices=[(b'Cost/Pricing', b'Cost/Pricing'), (b'Quality', b'Quality'), (b'Delivery', b'Delivery'), (b'Terms', b'Terms'), (b'Responsiveness', b'Responsiveness')], default='Total', max_length=15),
        ),
        migrations.AlterField(
            model_name='rating',
            name='score',
            field=models.IntegerField(choices=[(1, b'Poor'), (2, b'Average'), (3, b'Great')]),
        ),
    ]