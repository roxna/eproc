# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-20 13:30
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0017_tax_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='DebitNote',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='eProc.Document')),
                ('cost_shipping', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cost_other', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_percent', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_percent', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_paid', models.BooleanField(default=False)),
                ('billing_add', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='debitnote_billed', to='eProc.Location')),
                ('invoices', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debit_notes', to='eProc.Invoice')),
                ('shipping_add', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='debitnote_shipped', to='eProc.Location')),
                ('vendor_co', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debitnote', to='eProc.VendorCo')),
            ],
            options={
                'abstract': False,
            },
            bases=('eProc.document',),
        ),
        migrations.CreateModel(
            name='DebitNoteItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.CharField(blank=True, max_length=150, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('debit_note', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='eProc.DebitNote')),
            ],
        ),
    ]
