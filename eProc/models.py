from __future__ import unicode_literals
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from eProc.managers import *


################################
###     COMPANY DETAILS     ### 
################################ 

# File will be uploaded to MEDIA_ROOT/<buyer_co_name>/<filename>
def co_logo_directory_path(instance, filename):
	return '{0}/logo/{1}'.format(instance.user.buyer_profile.company.name, filename)

class Company (models.Model):
	name = models.CharField(max_length=30)	
	industry = models.CharField(choices=settings.INDUSTRY_CHOICES, max_length=20, null=True, blank=True)
	currency = models.CharField(choices=settings.CURRENCIES, max_length=10, null=True, blank=True)
	website = models.CharField(max_length=100, null=True, blank=True)	
	logo = models.ImageField(upload_to=co_logo_directory_path, default='../static/img/default_logo.jpg', blank=True, null=True)

	def __unicode__(self):
		return "{}".format(self.name)

	def get_primary_location(self):
	    return self.locations.last

	def get_all_locations(self):
		return [location for location in self.locations.all()]

class BuyerCo(Company):
	pass

class VendorCo(Company):
	contact_rep = models.CharField(max_length=150, null=True, blank=True)
	vendorID = models.CharField(max_length=50, null=True, blank=True)
	bank_name = models.CharField(max_length=50, null=True, blank=True)
	branch_details = models.CharField(max_length=50, null=True, blank=True)
	ac_number = models.BigIntegerField(null=True, blank=True)
	company_number = models.CharField(max_length=20, null=True, blank=True)
	comments = models.CharField(max_length=150, null=True, blank=True)
	buyer_co = models.ForeignKey(BuyerCo, related_name="vendor_cos", null=True, blank=True)

	def get_model_fields(model):
	    return model._meta.fields

class Location(models.Model):
	name = models.CharField(max_length=50, default='')
	loc_type = models.CharField(choices=settings.LOCATION_TYPES, max_length=20, default='HQ')	
	address1 = models.CharField(max_length=40, null=True, blank=True)
	address2 = models.CharField(max_length=40, default='-')
	city = models.CharField(max_length=20, null=True, blank=True)
	state = models.CharField(max_length=20, null=True, blank=True)
	country = models.CharField(choices=settings.COUNTRIES, max_length=20, null=True, blank=True)
	zipcode = models.CharField(max_length=10, null=True, blank=True)
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.")
	phone = models.CharField(max_length=15, validators=[phone_regex], null=True, blank=True)
	fax = models.BigIntegerField(null=True, blank=True)
	email = models.EmailField(max_length=254, null=True, blank=True)
	company = models.ForeignKey(Company, related_name="locations", null=True, blank=True)

	def __unicode__(self):
		return "{}".format(self.name)
		# return "{} \n {} \n {}, {} {}, {}".format(self.address1, self.address2, self.city, self.state, self.zipcode, self.country)


################################
###   ACCOUNTING DETAILS     ### 
################################ 

class Department(models.Model):
	name = models.CharField(max_length=50)
	budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	location = models.ForeignKey(Location, related_name='departments')

	def __unicode__(self):
		return "{}".format(self.name)

	# Total amount approved for spend or actually spent
	def get_spend_approved_ytd(self):
		spend = 0
		for requisition in self.requisitions.all():
			spend += requisition.get_spend_approved_ytd()
		return spend

	def get_spend_percent_of_budget(self):
		try:
			return "{} %".format(self.get_spend_approved_ytd()/self.budget*100)
		except ZeroDivisionError:
			return "No budget defined"

class AccountCode(models.Model):
	code = models.CharField(max_length=20)
	name = models.CharField(max_length=20)
	expense_type = models.CharField(choices=settings.EXPENSE_TYPES, max_length=20, default='Expense')
	company = models.ForeignKey(BuyerCo, related_name='account_codes')
	departments = models.ManyToManyField(Department, related_name='account_codes')
	
	def __unicode__(self):
		return "[{}] {}".format(self.code, self.name)

class Tax(models.Model):
	name = models.CharField(max_length=15)
	percent = models.DecimalField(max_digits=10, decimal_places=2)

	def __unicode__(self):
		return "{} ({}%)".format(self.name, self.percent)


################################
###           USERS          ### 
################################ 

# File will be uploaded to MEDIA_ROOT/<buyer_co_name>/<filename>
def user_img_directory_path(instance, filename):
	return '{0}/profile_pics/{1}_{2}'.format(instance.user.buyer_profile.company.name, instance.user.id, filename)

class User(AbstractUser):
    # Already has username, firstname, lastname, email, is_staff, is_active, date_joined    
    title = models.CharField(max_length=100, null=True, blank=True)
    profile_pic = models.ImageField(upload_to=user_img_directory_path, default='../static/img/default_profile_pic.jpg', blank=True, null=True)

    def __unicode__(self):
    	return self.username

class BuyerProfile(models.Model):
	role = models.CharField(choices=settings.ROLES, max_length=15)
	approval_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
	user = models.OneToOneField(User, related_name="buyer_profile")	
	department = models.ForeignKey(Department, related_name="users", null=True, blank=True)
	company = models.ForeignKey(BuyerCo, related_name="users")
	location = models.ForeignKey(Location, related_name="users")		

	def __unicode__(self):
		return "{}".format(self.user.username)


################################
###        DOCUMENTS         ### 
################################ 

class Document(models.Model):
	number = models.CharField(max_length=20)
	title = models.CharField(max_length=32, null=True, blank=True)
	date_created = models.DateTimeField(default=timezone.now)
	date_issued = models.DateTimeField(default=timezone.now, null=True, blank=True)
	date_due = models.DateField(default=timezone.now)
	currency = models.CharField(choices=settings.CURRENCIES, default='USD', max_length=10)
	sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	comments = models.CharField(max_length=100, null=True, blank=True)
	terms = models.CharField(max_length=5000, null=True, blank=True)
	preparer = models.ForeignKey(BuyerProfile, related_name="%(class)s_prepared_by")
	next_approver = models.ForeignKey(BuyerProfile, related_name="%(class)s_to_approve", null=True, blank=True)	
	buyer_co = models.ForeignKey(BuyerCo, related_name="%(class)s")
	
	# Managers - overridden in managers.py
	objects = models.Manager() # default manager
	latest_status_objects = LatestStatusManager() # manager to get approved/pending etc objects
	
	def __unicode__(self):
		return "{}".format(self.number)

	def get_latest_status(self):
	    return self.status_updates.latest('date')

	def get_status_with_value(self, value):
		return self.status_updates.filter(value=value).order_by('-date')[0]

	def is_past_due(self):
		if timezone.now().date() > self.date_due:
			return True
		return False

class SalesOrder(Document):
	cost_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	cost_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	discount_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	tax_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)	
	billing_add = models.ForeignKey(Location, related_name="%(class)s_billed")
	shipping_add = models.ForeignKey(Location, related_name="%(class)s_shipped")
	vendor_co = models.ForeignKey(VendorCo, related_name="%(class)s")

 	class Meta:
 		abstract = True	

 	def get_grand_total(self):
 		return self.sub_total + self.cost_shipping + self.cost_other + self.tax_amount - self.discount_amount

class Requisition(Document):
	department = models.ForeignKey(Department, related_name='requisitions')

	def get_spend_approved_ytd(self):
		spend = 0
		for item in self.items.all():
			spend += item.get_approved_subtotal()
		return spend

class PurchaseOrder(SalesOrder):	
	pass	

	def is_ready_to_close(self):
		for item in self.items.all():
			if item.qty_ordered != item.qty_delivered + item.qty_returned:
				return False
		return True

class Invoice(SalesOrder):
	purchase_order = models.ForeignKey(PurchaseOrder, related_name="invoices")	

class Drawdown(Document):
	location = models.ForeignKey(Location, related_name='drawdowns')

# File will be uploaded to MEDIA_ROOT/<buyer_co_name>/docs/<filename>
def file_directory_path(instance, filename):	    
	    return '{0}/docs/{1}'.format(instance.document.buyer_co.name, filename)

class File(models.Model):
	name = models.CharField(max_length=50, blank=True, null=True)
	file = models.FileField(upload_to=file_directory_path)
	comments = models.CharField(max_length=100, blank=True, null=True)
	document = models.ForeignKey(Document, related_name='files', blank=True, null=True)
	# company = models.ForeignKey(BuyerCo, related_name="attachments")

	def __unicode__(self):
		return "{}".format(self.name)


##########################################
###    PRODUCT & ORDER LINE ITEMS      ### 
########################################## 

class Category(models.Model):
	code = models.IntegerField(null=True, blank=True)
	name = models.CharField(max_length=50)
	buyer_co = models.ForeignKey(BuyerCo, related_name="categories")

	def __unicode__(self):
		return "{}".format(self.name)

class CatalogItem(models.Model):
	name = models.CharField(max_length=50)
	desc = models.CharField(max_length=150, null=True, blank=True)
	sku = models.CharField(max_length=20, null=True, blank=True)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	unit_type = models.CharField(max_length=20, default="each")
	threshold = models.IntegerField(null=True, blank=True) # Alert if inventory drops below
	currency = models.CharField(choices=settings.CURRENCIES, default='USD', max_length=10)
	category = models.ForeignKey(Category, related_name="catalog_items")
	vendor_co = models.ForeignKey(VendorCo, related_name="catalog_items")
	buyer_co = models.ForeignKey(BuyerCo, related_name="catalog_items")

	def __unicode__(self):
		return "{}".format(self.name)

class Item(models.Model):
	qty_requested = models.IntegerField(default=1) 	
	qty_approved = models.IntegerField(null=True, blank=True, default=0)
	product = models.ForeignKey(CatalogItem, related_name='items')
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	number = models.CharField(max_length=20)
	comments_request = models.CharField(max_length=500, blank=True, null=True)
	comments_approved = models.CharField(max_length=500, blank=True, null=True)
	date_due = models.DateField(default=timezone.now)

	# Managers - overridden in managers.py
	objects = models.Manager() # default manager
	latest_status_objects = LatestStatusManager() # manager to get approved/pending etc objects

	# class Meta:
	# 	abstract = True

	def get_requested_date(self):
	    return self.status_updates.filter(value='Pending').date

	def get_approved_date(self):
	    return self.status_updates.filter(value='Approved').date
	
	def is_past_due(self):
		if timezone.now().date() > self.date_due:
			return True
		return False

	def get_latest_status(self):
	    return self.status_updates.latest('date')	

class OrderItem(Item):		
	qty_ordered = models.IntegerField(null=True, blank=True, default=0)
	qty_delivered = models.IntegerField(null=True, blank=True, default=0)
	qty_returned = models.IntegerField(null=True, blank=True, default=0)	
	comments_order = models.CharField(max_length=500, blank=True, null=True)	
	comments_delivery = models.CharField(max_length=500, blank=True, null=True)		
	tax = models.ForeignKey(Tax, related_name='items', null=True, blank=True)
	account_code = models.ForeignKey(AccountCode, related_name="items", null=True, blank=True)	
	requisition = models.ForeignKey(Requisition, related_name='items', null=True, blank=True)
	purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', null=True, blank=True)
	invoice = models.ForeignKey(Invoice, related_name='items', null=True, blank=True)
	
	def __unicode__(self):
		return "{} at {} {} [{} req, {} approved]".format(self.product.name, self.product.currency, self.unit_price, self.qty_requested, self.qty_approved)

	def get_unit_price(self):
		return self.unit_price

	# Helper function for all get_x_subtotal functions
	def get_subtotal(self, price, quantity):
		try:
			return price * quantity
		except TypeError: #If qty is not defined
			return '-'

	def get_requested_subtotal(self):
		return self.get_subtotal(self.unit_price, self.qty_requested)
	
	def get_approved_subtotal(self):
		return self.get_subtotal(self.unit_price, self.qty_approved)

	def get_ordered_subtotal(self):
		return self.get_subtotal(self.unit_price, self.qty_ordered)

	def get_delivered_subtotal(self):
		return self.get_subtotal(self.unit_price, self.qty_delivered)

	def get_refund_subtotal(self):
		return self.get_subtotal(self.unit_price, self.qty_returned)

	def get_delivered_date(self):
	    return self.status_updates.filter(value__in=['Delivered Partial', 'Delivered Complete']).order_by('-date')[0].date
	

class DrawdownItem(Item):
	qty_drawndown = models.IntegerField(null=True, blank=True, default=0)
	drawdown = models.ForeignKey(Drawdown, related_name='items', null=True, blank=True)
	comments_drawdown = models.CharField(max_length=500, blank=True, null=True)

	def get_drawdown_date(self):
	    return self.status_updates.filter(value='Drawdown').date

##########################################
#####      STATUS (DOC & ITEM)       ##### 
########################################## 

class Status(models.Model):
	value = models.CharField(max_length=20, choices=settings.STATUSES, default='Pending')
	date = models.DateTimeField(editable=False, default=timezone.now)
	author = models.ForeignKey(BuyerProfile, related_name="%(class)s_updates")

	def __unicode__(self):
		return "{}".format(self.value)

	def get_author(self):
		return self.author

	def get_status_details(self):
		return "{} ({})".format(self.author, self.date.date())

	class Meta:
		abstract = True
		get_latest_by = 'date'

class DocumentStatus(Status):
	document = models.ForeignKey(Document, related_name="status_updates")

class OrderItemStatus(Status):
	item = models.ForeignKey(OrderItem, related_name='status_updates')

class DrawdownItemStatus(Status):
	item = models.ForeignKey(DrawdownItem, related_name='status_updates')

##########################################
#####           RATINGS              ##### 
########################################## 

class Rating(models.Model):
	SCORES = (
		(1, 'Awful'),
		(2, 'Bad'),
		(3, 'Ok'),
		(4, 'Good'),
		(5, 'Great'),
	)
	score = models.IntegerField(choices=SCORES)
	CATEGORIES = (
		('Quality', 'Quality'),
		('Delivery', 'Delivery'),
		('Cost', 'Cost'),
		('Responsiveness', 'Responsiveness'),
		('Total', 'Total'),
	)
	category = models.CharField(choices=CATEGORIES, max_length=15, default='Total')
	rater = models.ForeignKey(Company, related_name="ratings_given")
	ratee = models.ForeignKey(Company, related_name="ratings_received")
	comments = models.CharField(max_length=100)

	def __unicode__(self):
		return "{} - {}".format(self.receiver, self.value)
