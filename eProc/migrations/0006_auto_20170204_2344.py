# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-04 23:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0005_auto_20170204_2125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='ratee',
        ),
        migrations.AddField(
            model_name='rating',
            name='vendor_co',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='eProc.VendorCo'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='rating',
            name='category',
            field=models.CharField(choices=[('Cost/Pricing', 'Cost/Pricing'), ('Quality', 'Quality'), ('Delivery', 'Delivery'), ('Terms', 'Terms'), ('Responsiveness', 'Responsiveness'), ('Total', 'Total')], default='Total', max_length=15),
        ),
        migrations.AlterField(
            model_name='rating',
            name='rater',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorco',
            name='contact_rep',
            field=models.CharField(default='-', max_length=150),
        ),
    ]