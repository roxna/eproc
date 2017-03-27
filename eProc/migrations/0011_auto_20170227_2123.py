# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-27 21:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0010_auto_20170227_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogItemRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('desc', models.CharField(blank=True, max_length=150, null=True)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit_type', models.CharField(default='each', max_length=20)),
                ('currency', models.CharField(choices=[(b'USD', b'USD'), (b'INR', b'INR')], default='USD', max_length=10)),
                ('max_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('buyer_cos', models.ManyToManyField(blank=True, null=True, related_name='catalogitemrequests', to='eProc.BuyerCo')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalogitemrequests', to='eProc.Category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='catalogitem',
            name='buyer_cos',
            field=models.ManyToManyField(blank=True, null=True, related_name='catalogitems', to='eProc.BuyerCo'),
        ),
        migrations.AlterField(
            model_name='catalogitem',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalogitems', to='eProc.Category'),
        ),
        migrations.AlterField(
            model_name='catalogitem',
            name='item_type',
            field=models.CharField(choices=[('Buyer Uploaded', 'Buyer Uploaded'), ('Bulk Discount', 'Bulk Discount')], default='Buyer Uploaded', max_length=20),
        ),
        migrations.AlterField(
            model_name='catalogitem',
            name='vendor_co',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalogitems', to='eProc.VendorCo'),
        ),
    ]