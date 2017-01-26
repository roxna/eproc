# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-26 00:26
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import eProc.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('profile_pic', models.ImageField(blank=True, default='../static/img/default_profile_pic.jpg', null=True, upload_to=eProc.models.user_img_directory_path)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AccountCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=20)),
                ('expense_type', models.CharField(choices=[(b'Asset', b'Asset'), (b'Expense', b'Expense')], default='Expense', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='BuyerProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[(b'SuperUser', b'SuperUser'), (b'Requester', b'Requester'), (b'Approver', b'Approver'), (b'Purchaser', b'Purchaser'), (b'Receiver', b'Receiver'), (b'Inventory Manager', b'Inventory Manager'), (b'Payer', b'Payer')], max_length=15)),
                ('approval_threshold', models.DecimalField(decimal_places=2, default=100.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='CatalogItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('desc', models.CharField(blank=True, max_length=150, null=True)),
                ('sku', models.CharField(blank=True, max_length=20, null=True)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit_type', models.CharField(default='each', max_length=20)),
                ('threshold', models.IntegerField(blank=True, null=True)),
                ('currency', models.CharField(choices=[(b'USD', b'USD'), (b'INR', b'INR')], default='USD', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('industry', models.CharField(blank=True, choices=[(b'Real Estate', b'Real Estate'), (b'Manufacturing', b'Manufacturing'), (b'Hospitals', b'Hospitals')], max_length=20, null=True)),
                ('currency', models.CharField(blank=True, choices=[(b'USD', b'USD'), (b'INR', b'INR')], max_length=10, null=True)),
                ('website', models.CharField(blank=True, max_length=100, null=True)),
                ('logo', models.ImageField(blank=True, default='../static/img/default_logo.jpg', null=True, upload_to=eProc.models.co_logo_directory_path)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('budget', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20)),
                ('title', models.CharField(blank=True, max_length=32, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_issued', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('date_due', models.DateField(default=django.utils.timezone.now)),
                ('currency', models.CharField(choices=[(b'USD', b'USD'), (b'INR', b'INR')], default='USD', max_length=10)),
                ('sub_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('comments', models.CharField(blank=True, max_length=100, null=True)),
                ('terms', models.CharField(blank=True, max_length=5000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(choices=[(b'Pending', b'Pending'), (b'Approved', b'Approved'), (b'Denied', b'Denied'), (b'Ordered', b'Ordered'), (b'Cancelled', b'Cancelled'), (b'Delivered Partial', b'Delivered Partial'), (b'Delivered Complete', b'Delivered Complete'), (b'Paid', b'Paid'), (b'Drawdown Partial', b'Drawdown Partial'), (b'Drawdown Complete', b'Drawdown Complete'), (b'Open', b'Open'), (b'Closed', b'Closed'), (b'Archived', b'Archived')], default='Pending', max_length=20)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentstatus_updates', to='eProc.BuyerProfile')),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'date',
            },
        ),
        migrations.CreateModel(
            name='DrawdownItemStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(choices=[(b'Pending', b'Pending'), (b'Approved', b'Approved'), (b'Denied', b'Denied'), (b'Ordered', b'Ordered'), (b'Cancelled', b'Cancelled'), (b'Delivered Partial', b'Delivered Partial'), (b'Delivered Complete', b'Delivered Complete'), (b'Paid', b'Paid'), (b'Drawdown Partial', b'Drawdown Partial'), (b'Drawdown Complete', b'Drawdown Complete'), (b'Open', b'Open'), (b'Closed', b'Closed'), (b'Archived', b'Archived')], default='Pending', max_length=20)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drawdownitemstatus_updates', to='eProc.BuyerProfile')),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'date',
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('file', models.FileField(upload_to=eProc.models.file_directory_path)),
                ('comments', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty_requested', models.IntegerField(default=1)),
                ('qty_approved', models.IntegerField(blank=True, default=0, null=True)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('number', models.CharField(max_length=20)),
                ('comments_request', models.CharField(blank=True, max_length=500, null=True)),
                ('comments_approved', models.CharField(blank=True, max_length=500, null=True)),
                ('date_due', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loc_type', models.CharField(choices=[(b'Billing', b'Billing'), (b'Shipping', b'Shipping'), (b'HQ', b'HQ')], default='Shipping', max_length=20)),
                ('name', models.CharField(default='', max_length=50)),
                ('address1', models.CharField(blank=True, max_length=40, null=True)),
                ('address2', models.CharField(blank=True, max_length=40, null=True)),
                ('city', models.CharField(blank=True, max_length=20, null=True)),
                ('state', models.CharField(blank=True, max_length=20, null=True)),
                ('country', models.CharField(blank=True, choices=[(b'India', b'India'), (b'USA', b'USA')], max_length=20, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=10, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('fax', models.BigIntegerField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItemStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(choices=[(b'Pending', b'Pending'), (b'Approved', b'Approved'), (b'Denied', b'Denied'), (b'Ordered', b'Ordered'), (b'Cancelled', b'Cancelled'), (b'Delivered Partial', b'Delivered Partial'), (b'Delivered Complete', b'Delivered Complete'), (b'Paid', b'Paid'), (b'Drawdown Partial', b'Drawdown Partial'), (b'Drawdown Complete', b'Drawdown Complete'), (b'Open', b'Open'), (b'Closed', b'Closed'), (b'Archived', b'Archived')], default='Pending', max_length=20)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderitemstatus_updates', to='eProc.BuyerProfile')),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'date',
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(choices=[(1, 'Awful'), (2, 'Bad'), (3, 'Ok'), (4, 'Good'), (5, 'Great')])),
                ('category', models.CharField(choices=[('Quality', 'Quality'), ('Delivery', 'Delivery'), ('Cost', 'Cost'), ('Responsiveness', 'Responsiveness'), ('Total', 'Total')], default='Total', max_length=15)),
                ('comments', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
                ('percent', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='BuyerCo',
            fields=[
                ('company_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='eProc.Company')),
            ],
            bases=('eProc.company',),
        ),
        migrations.CreateModel(
            name='Drawdown',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='eProc.Document')),
            ],
            bases=('eProc.document',),
        ),
        migrations.CreateModel(
            name='DrawdownItem',
            fields=[
                ('item_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='eProc.Item')),
                ('qty_drawndown', models.IntegerField(blank=True, default=0, null=True)),
                ('comments_drawdown', models.CharField(blank=True, max_length=500, null=True)),
                ('drawdown', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='eProc.Drawdown')),
            ],
            bases=('eProc.item',),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='eProc.Document')),
                ('cost_shipping', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cost_other', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_percent', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_percent', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('grand_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('eProc.document',),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('item_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='eProc.Item')),
                ('qty_ordered', models.IntegerField(blank=True, default=0, null=True)),
                ('qty_delivered', models.IntegerField(blank=True, default=0, null=True)),
                ('qty_returned', models.IntegerField(blank=True, default=0, null=True)),
                ('comments_order', models.CharField(blank=True, max_length=500, null=True)),
                ('comments_delivery', models.CharField(blank=True, max_length=500, null=True)),
            ],
            bases=('eProc.item',),
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='eProc.Document')),
                ('cost_shipping', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cost_other', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_percent', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_percent', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('grand_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('eProc.document',),
        ),
        migrations.CreateModel(
            name='Requisition',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='eProc.Document')),
            ],
            bases=('eProc.document',),
        ),
        migrations.CreateModel(
            name='VendorCo',
            fields=[
                ('company_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='eProc.Company')),
                ('contact_rep', models.CharField(blank=True, max_length=150, null=True)),
                ('vendorID', models.CharField(blank=True, max_length=50, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=50, null=True)),
                ('branch_details', models.CharField(blank=True, max_length=50, null=True)),
                ('ac_number', models.BigIntegerField(blank=True, null=True)),
                ('company_number', models.CharField(blank=True, max_length=20, null=True)),
                ('comments', models.CharField(blank=True, max_length=150, null=True)),
                ('buyer_co', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vendor_cos', to='eProc.BuyerCo')),
            ],
            bases=('eProc.company',),
        ),
        migrations.AddField(
            model_name='rating',
            name='ratee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings_received', to='eProc.Company'),
        ),
        migrations.AddField(
            model_name='rating',
            name='rater',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings_given', to='eProc.Company'),
        ),
        migrations.AddField(
            model_name='location',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='eProc.Company'),
        ),
        migrations.AddField(
            model_name='item',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='eProc.CatalogItem'),
        ),
        migrations.AddField(
            model_name='file',
            name='document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='eProc.Document'),
        ),
        migrations.AddField(
            model_name='documentstatus',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_updates', to='eProc.Document'),
        ),
        migrations.AddField(
            model_name='document',
            name='next_approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='document_to_approve', to='eProc.BuyerProfile'),
        ),
        migrations.AddField(
            model_name='document',
            name='preparer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document_prepared_by', to='eProc.BuyerProfile'),
        ),
        migrations.AddField(
            model_name='department',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='eProc.Location'),
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalog_items', to='eProc.Category'),
        ),
        migrations.AddField(
            model_name='buyerprofile',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='eProc.Department'),
        ),
        migrations.AddField(
            model_name='buyerprofile',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='eProc.Location'),
        ),
        migrations.AddField(
            model_name='buyerprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accountcode',
            name='departments',
            field=models.ManyToManyField(related_name='account_codes', to='eProc.Department'),
        ),
        migrations.AddField(
            model_name='requisition',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requisitions', to='eProc.Department'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='billing_add',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchaseorder_billed', to='eProc.Location'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='shipping_add',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchaseorder_shipped', to='eProc.Location'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='vendor_co',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchaseorder', to='eProc.VendorCo'),
        ),
        migrations.AddField(
            model_name='orderitemstatus',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_updates', to='eProc.OrderItem'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='account_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='eProc.AccountCode'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='eProc.Invoice'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='purchase_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='eProc.PurchaseOrder'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='requisition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='eProc.Requisition'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='tax',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='eProc.Tax'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='billing_add',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice_billed', to='eProc.Location'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='purchase_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='eProc.PurchaseOrder'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='shipping_add',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice_shipped', to='eProc.Location'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='vendor_co',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='eProc.VendorCo'),
        ),
        migrations.AddField(
            model_name='drawdownitemstatus',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_updates', to='eProc.DrawdownItem'),
        ),
        migrations.AddField(
            model_name='drawdown',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drawdowns', to='eProc.Location'),
        ),
        migrations.AddField(
            model_name='document',
            name='buyer_co',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document', to='eProc.BuyerCo'),
        ),
        migrations.AddField(
            model_name='category',
            name='buyer_co',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='eProc.BuyerCo'),
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='buyer_co',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalog_items', to='eProc.BuyerCo'),
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='vendor_co',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalog_items', to='eProc.VendorCo'),
        ),
        migrations.AddField(
            model_name='buyerprofile',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='eProc.BuyerCo'),
        ),
        migrations.AddField(
            model_name='accountcode',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_codes', to='eProc.BuyerCo'),
        ),
    ]
