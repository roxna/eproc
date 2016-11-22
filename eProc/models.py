from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from eProc.managers import *


######### COMPANY DETAILS #########
class Company (models.Model):
	name = models.CharField(max_length=30)	
	currency = models.CharField(choices=settings.CURRENCIES, max_length=10, null=True, blank=True)
	logo = models.ImageField(upload_to='logos', default='../static/img/default_logo.jpg', blank=True, null=True)

	def __unicode__(self):
		return "{}".format(self.name)


class BuyerCo(Company):
	pass

class VendorCo(Company):
	bank_name = models.CharField(max_length=50, null=True, blank=True)
	branch_details = models.CharField(max_length=50, null=True, blank=True)
	ac_number = models.BigIntegerField(null=True, blank=True)
	company_number = models.CharField(max_length=20, null=True, blank=True)
	buyer_co = models.ForeignKey(BuyerCo, related_name="vendor_cos", null=True, blank=True)	

class Location(models.Model):
	name = models.CharField(max_length=20, default='HQ')
	typee = models.CharField(choices=settings.LOCATION_TYPES, max_length=15, default='Billing')
	address1 = models.CharField(max_length=40, null=True, blank=True)
	address2 = models.CharField(max_length=40, null=True, blank=True)
	city = models.CharField(max_length=20, null=True, blank=True)
	state = models.CharField(max_length=20, null=True, blank=True)
	country = models.CharField(choices=settings.COUNTRIES, max_length=20, null=True, blank=True)
	zipcode = models.IntegerField(null=True, blank=True)
	phone = models.BigIntegerField(null=True, blank=True)
	email = models.EmailField(max_length=254, null=True, blank=True)
	company = models.ForeignKey(Company, related_name="locations")

	def __unicode__(self):
		return "{} \n {} \n {}, {} {}, {}".format(self.address1, self.address2, self.city, self.state, self.zipcode, self.country)

	def get_primary_location(self):
		primary_location = Location.objects.filter(typee='HQ')[0]
		if primary_location:
			return primary_location 


######### ACCOUNTING DETAILS #########
class Department(models.Model):
	name = models.CharField(max_length=20)
	company = models.ForeignKey(BuyerCo, related_name='departments')

	def __unicode__(self):
		return "{}".format(self.name)

class AccountCode(models.Model):
	code = models.CharField(max_length=20)
	category = models.CharField(max_length=20)
	description = models.CharField(max_length=50, null=True, blank=True)
	company = models.ForeignKey(BuyerCo, related_name='account_codes')
	
	def __unicode__(self):
		return "[{}] {}".format(self.code, self.category)

class Tax(models.Model):
	name = models.CharField(max_length=15)
	percent = models.DecimalField(max_digits=10, decimal_places=2)

	def __unicode__(self):
		return "{} ({}%)".format(self.name, self.percent)


########## USERS  #########
class User(AbstractUser):
    # Already has username, firstname, lastname, email, is_staff, is_active, date_joined    
    # profile_pic = models.ImageField(upload_to='profile_pics', default='../static/img/default_profile_pic.jpg', blank=True, null=True)

    def __unicode__(self):
    	return self.username

class BuyerProfile(models.Model):
	role = models.CharField(choices=settings.ROLES, max_length=15)
	user = models.OneToOneField(User, related_name="buyer_profile")	
	department = models.ForeignKey(Department, related_name="users", null=True, blank=True)
	company = models.ForeignKey(BuyerCo, related_name="users")

	def __unicode__(self):
		return "{}".format(self.user.username)

class VendorProfile(models.Model):
	user = models.OneToOneField(User, related_name="vendor_profile")
	company = models.ForeignKey(VendorCo, related_name="users")

	def __unicode__(self):
		return "{}".format(self.user.username)


########## ORDERS - REQUISITION, PO, INVOICE  #########
class Document(models.Model):
	number = models.CharField(max_length=20)
	title = models.CharField(max_length=32, null=True, blank=True)
	date_created = models.DateTimeField(default=timezone.now)
	date_issued = models.DateTimeField(default=timezone.now, null=True, blank=True)
	date_due = models.DateField(default=timezone.now)
	currency = models.CharField(choices=settings.CURRENCIES, default='USD', max_length=10)
	sub_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	comments = models.CharField(max_length=100, null=True, blank=True)
	preparer = models.ForeignKey(BuyerProfile, related_name="%(class)s_prepared_by")
	next_approver = models.ForeignKey(BuyerProfile, related_name="%(class)s_to_approve", null=True, blank=True)	
	buyerCo = models.ForeignKey(BuyerCo, related_name="%(class)s")
	
	def get_latest_status(self):	    
	    latest_status = None
	    for status in self.status_updates.all():
	        if latest_status is None or latest_status.date < status.date:
	            latest_status = status
	    return latest_status

class SalesOrder(models.Model):
	cost_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	cost_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	discount_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	tax_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	terms = models.CharField(max_length=5000, blank=True, null=True)	
	billing_add = models.ForeignKey(Location, related_name="%(class)s_billed")
	shipping_add = models.ForeignKey(Location, related_name="%(class)s_shipped")
	vendorCo = models.ForeignKey(VendorCo, related_name="%(class)s_orders")

 	class Meta:
 		abstract = True	

class Requisition(Document):
	department = models.ForeignKey(Department, related_name='requisitions')

	def __unicode__(self):
		return "Requisition No. {}".format(self.number)

class PurchaseOrder(Document, SalesOrder):	
	def __unicode__(self):
		return "PO No. {}".format(self.number)

class Invoice(Document, SalesOrder):
	is_paid = models.BooleanField(default=False)
	purchase_order = models.ForeignKey(PurchaseOrder, related_name="invoices")	

	def __unicode__(self):
		return "Invoice No. {}".format(self.number)	


######### PRODUCT & ORDER LINE ITEMS #########
class Category(models.Model):
	code = models.IntegerField(null=True, blank=True)
	name = models.CharField(max_length=50)
	buyerCo = models.ForeignKey(BuyerCo, related_name="categories")

	def __unicode__(self):
		return "{}".format(self.name)

class CatalogItem(models.Model):
	name = models.CharField(max_length=50)
	desc = models.CharField(max_length=150, null=True, blank=True)
	sku = models.CharField(max_length=20)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	unit_type = models.CharField(max_length=20, default="each")
	currency = models.CharField(choices=settings.CURRENCIES, default='USD', max_length=10)
	category = models.ForeignKey(Category, related_name="catalog_items")
	vendorCo = models.ForeignKey(VendorCo, related_name="catalog_items")
	buyerCo = models.ForeignKey(BuyerCo, related_name="catalog_items")

	def __unicode__(self):
		return "{}".format(self.name)

class OrderItem(models.Model):
	number = models.CharField(max_length=20)
	quantity = models.IntegerField(default=1)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	sub_total = models.DecimalField(max_digits=10, decimal_places=2)
	comments = models.CharField(max_length=150, blank=True, null=True)		
	is_approved = models.BooleanField(default=False)
	date_due = models.DateField(default=timezone.now)
	tax = models.ForeignKey(Tax, related_name='order_items', null=True, blank=True)
	account_code = models.ForeignKey(AccountCode, related_name="order_items")
	product = models.ForeignKey(CatalogItem, related_name='order_items')
	requisition = models.ForeignKey(Requisition, related_name='order_items')
	purchase_order = models.ForeignKey(PurchaseOrder, related_name='order_items', null=True, blank=True) # If order_item is part of a PO, no longer 'pending'

	def __unicode__(self):
		return "{} of {} at {} {}".format(self.quantity, self.product.name, self.product.currency, self.unit_price)

	def get_unit_price(self):
		return self.unit_price

######### OTHER DETAILS #########
class Status(models.Model):
	STATUS = (
		# Requisitions
		('Draft', 'Draft'),
		('Pending', 'Pending'),
		('Approved', 'Approved'),
		('Denied', 'Denied'),
		# POs
		('Open', 'Open'),
		('Closed', 'Closed'),
		('Cancelled', 'Cancelled'),
		('Paid', 'Paid'),
		# All 
		('Archived', 'Archived'),
	)
	COLORS = (
		('Pending', 'yellow'),
		('Approved', 'green'),
		('Denied', 'red'),
		('Other', 'grey')
	)
	value = models.CharField(max_length=10, choices=STATUS, default='Draft')
	color = models.CharField(max_length=10, choices=COLORS, default='Other')
	date = models.DateTimeField(editable=False, default=timezone.now)
	author = models.ForeignKey(BuyerProfile, related_name="status_updates")
	document = models.ForeignKey(Document, related_name="status_updates")

	def __unicode__(self):
		return "{}".format(self.value)

class Rating(models.Model):
	SCORES = (
		(1, 'Awful'),
		(2, 'Bad'),
		(3, 'Ok'),
		(4, 'Good'),
		(5, 'Great'),
	)
	score = models.IntegerField(choices=SCORES)
	company = models.ForeignKey(Company, related_name="ratings")
	comments = models.CharField(max_length=100)

class Attachment(models.Model):
	name = models.CharField(max_length=50)
	file = models.FileField(upload_to='/docs', blank=True, null=True)
	company = models.ForeignKey(VendorCo, related_name="attachments")

	def __unicode__(self):
		return "{}".format(self.name)	

