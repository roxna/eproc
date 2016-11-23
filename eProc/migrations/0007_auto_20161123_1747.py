# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-23 17:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eProc', '0006_auto_20161123_0325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountcode',
            name='company',
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='company',
        ),
        migrations.RemoveField(
            model_name='buyerco',
            name='company_ptr',
        ),
        migrations.RemoveField(
            model_name='buyerprofile',
            name='company',
        ),
        migrations.RemoveField(
            model_name='buyerprofile',
            name='department',
        ),
        migrations.RemoveField(
            model_name='buyerprofile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='catalogitem',
            name='buyer_co',
        ),
        migrations.RemoveField(
            model_name='catalogitem',
            name='category',
        ),
        migrations.RemoveField(
            model_name='catalogitem',
            name='vendor_co',
        ),
        migrations.RemoveField(
            model_name='category',
            name='buyer_co',
        ),
        migrations.RemoveField(
            model_name='department',
            name='company',
        ),
        migrations.RemoveField(
            model_name='document',
            name='buyer_co',
        ),
        migrations.RemoveField(
            model_name='document',
            name='next_approver',
        ),
        migrations.RemoveField(
            model_name='document',
            name='preparer',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='billing_add',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='document_ptr',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='purchase_order',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='shipping_add',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='vendor_co',
        ),
        migrations.RemoveField(
            model_name='location',
            name='company',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='account_code',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='product',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='purchase_order',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='requisition',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='tax',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='billing_add',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='document_ptr',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='shipping_add',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='vendor_co',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='company',
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='department',
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='document_ptr',
        ),
        migrations.RemoveField(
            model_name='status',
            name='author',
        ),
        migrations.RemoveField(
            model_name='status',
            name='document',
        ),
        migrations.RemoveField(
            model_name='vendorco',
            name='buyer_co',
        ),
        migrations.RemoveField(
            model_name='vendorco',
            name='company_ptr',
        ),
        migrations.RemoveField(
            model_name='vendorprofile',
            name='company',
        ),
        migrations.RemoveField(
            model_name='vendorprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='AccountCode',
        ),
        migrations.DeleteModel(
            name='Attachment',
        ),
        migrations.DeleteModel(
            name='BuyerCo',
        ),
        migrations.DeleteModel(
            name='BuyerProfile',
        ),
        migrations.DeleteModel(
            name='CatalogItem',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Company',
        ),
        migrations.DeleteModel(
            name='Department',
        ),
        migrations.DeleteModel(
            name='Document',
        ),
        migrations.DeleteModel(
            name='Invoice',
        ),
        migrations.DeleteModel(
            name='Location',
        ),
        migrations.DeleteModel(
            name='OrderItem',
        ),
        migrations.DeleteModel(
            name='PurchaseOrder',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
        migrations.DeleteModel(
            name='Requisition',
        ),
        migrations.DeleteModel(
            name='Status',
        ),
        migrations.DeleteModel(
            name='Tax',
        ),
        migrations.DeleteModel(
            name='VendorCo',
        ),
        migrations.DeleteModel(
            name='VendorProfile',
        ),
    ]
