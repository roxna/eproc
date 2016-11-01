from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


######### COMPANY DETAILS #########
class Company (models.Model):
	name = models.CharField(max_length=30)
	logo = models.ImageField(upload_to='logos', default='../static/img/default_logo.jpg', blank=True, null=True)

class BuyerCo(Company):
	def __unicode__(self):
		return "Buyer: {}".format(self.name)

class VendorCo(Company):
	bank_name = models.CharField(max_length=50, null=True, blank=True)
	branch_details = models.CharField(max_length=50, null=True, blank=True)
	ac_number = models.BigIntegerField(null=True, blank=True)
	company_number = models.CharField(max_length=20, null=True, blank=True)
	buyer_cos = models.ManyToManyField(BuyerCo, related_name="vendor_cos")	
	
	def __unicode__(self):
		return "Vendor: {}".format(self.name)

class Location(models.Model):
	name = models.CharField(max_length=20)
	address1 = models.CharField(max_length=40)
	address2 = models.CharField(max_length=40)
	city = models.CharField(max_length=20)
	state = models.CharField(max_length=20)
	country = models.CharField(max_length=20)
	zipcode = models.IntegerField(default=94123)
	phone = models.BigIntegerField(default=0)
	email = models.EmailField(max_length=254)
	company = models.ForeignKey(Company, related_name="locations")

	def __unicode__(self):
		return "{} - {}".format(self.company.name, self.name)


######### ACCOUNTING DETAILS #########
class Department(models.Model):
	name = models.CharField(max_length=20)
	company = models.ForeignKey(BuyerCo, related_name='departments')

	def __unicode__(self):
		return "{}".format(self.name)

class AccountCode(models.Model):
	code = models.CharField(max_length=20)
	category = models.CharField(max_length=20, null=True, blank=True)
	description = models.CharField(max_length=50)
	
	def __unicode__(self):
		return "{}".format(self.code)

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
	ROLES = (
		(1, 'SuperUser'),
		(2, 'Requester'),
		(3, 'Approver'),
		(4, 'Purchaser'),
		(5, 'Receiver'),
		(6, 'Payer'),
	)
	role = models.IntegerField(choices=ROLES)
	user = models.OneToOneField(User, related_name="buyer_profile")	
	department = models.ForeignKey(Department, related_name="users", null=True, blank=True)
	company = models.ForeignKey(BuyerCo, related_name="users")

	def __unicode__(self):
		return "Buyer: {} [{}] [{}]".format(self.user.username, self.get_role_display(), self.company.name)

class VendorProfile(models.Model):
	user = models.OneToOneField(User, related_name="vendor_profile")
	company = models.ForeignKey(VendorCo, related_name="users")

	def __unicode__(self):
		return "Vendor: {} [{}]".format(self.user.username, self.company.name)


########## ORDERS - REQUISITION, PO, INVOICE  #########
class Document(models.Model):
	number = models.CharField(max_length=20)
	title = models.CharField(max_length=32, null=True, blank=True)
	date_created = models.DateTimeField(default=timezone.now)
	date_issued = models.DateTimeField(default=timezone.now, null=True, blank=True)
	date_due = models.DateField(default=timezone.now)
	currency = models.CharField(max_length=3, default="USD")
	sub_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	comments = models.CharField(max_length=100, null=True, blank=True)
	preparer = models.ForeignKey(BuyerProfile, related_name="%(class)s_prepared_by")
	next_approver = models.ForeignKey(BuyerProfile, related_name="%(class)s_to_approve", null=True, blank=True)	
	buyerCo = models.ForeignKey(BuyerCo, related_name="%(class)s")

class SalesOrder(models.Model):
	cost_shipping = models.DecimalField(max_digits=10, decimal_places=2)
	cost_other = models.DecimalField(max_digits=10, decimal_places=2)
	discount_percent = models.DecimalField(max_digits=10, decimal_places=2)
	discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
	tax_percent = models.DecimalField(max_digits=10, decimal_places=2)
	tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
	grand_total = models.DecimalField(max_digits=10, decimal_places=2)
	terms = models.CharField(max_length=5000, null=True)	
	billing_add = models.ForeignKey(Location, related_name="%(class)s_billed")
	shipping_add = models.ForeignKey(Location, related_name="%(class)s_shipped")
	vendorCo = models.ForeignKey(VendorCo, related_name="%(class)s_orders")

 	class Meta:
 		abstract = True	

class Requisition(Document):
	department = models.ForeignKey(Department, related_name='requisitions')

	def __unicode__(self):
		return "Requisition No. {} [{}]".format(self.number, self.date_issued)

class PurchaseOrder(Document, SalesOrder):	
	def __unicode__(self):
		return "PO No. {} [{}]".format(self.number, self.date_issued)	

class Invoice(Document, SalesOrder):
	is_paid = models.BooleanField(default=False)
	purchase_order = models.ForeignKey(PurchaseOrder, related_name="invoices")	

	def __unicode__(self):
		return "Invoice No. {} [{}]".format(self.number, self.date_issued)	


######### PRODUCT & ORDER LINE ITEMS #########
class Category(models.Model):
	code = models.IntegerField()
	name = models.CharField(max_length=50)

	def __unicode__(self):
		return "[{}] {}".format(self.code, self.name)

class CatalogItem(models.Model):
	name = models.CharField(max_length=50)
	desc = models.CharField(max_length=150, null=True, blank=True)
	sku = models.CharField(max_length=20)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	unit_type = models.CharField(max_length=20)	
	currency = models.CharField(max_length=20)
	category = models.ForeignKey(Category, related_name="catalog_items")
	vendorCo = models.ForeignKey(VendorCo, related_name="catalog_items")

	def __unicode__(self):
		return "{}".format(self.name)

class OrderItem(models.Model):
	quantity = models.IntegerField(default=1)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	sub_total = models.DecimalField(max_digits=10, decimal_places=2)
	comments = models.CharField(max_length=150)		
	is_approved = models.BooleanField(default=False)
	tax = models.ForeignKey(Tax, related_name='order_items', null=True, blank=True)
	account_code = models.ForeignKey(AccountCode, related_name="order_items")
	product = models.ForeignKey(CatalogItem, related_name='order_items')
	requisition = models.ForeignKey(Requisition, related_name='order_items', null=True, blank=True)
	purchase_order = models.ForeignKey(PurchaseOrder, related_name='order_items', null=True, blank=True)

	def __unicode__(self):
		return "{} of {} at {}{}".format(self.quantity, self.product.name, self.product.currency, self.unit_price)

######### OTHER DETAILS #########
class Status(models.Model):
	STATUS = (
		(1, 'Draft'),
		(2, 'Pending'),
		(3, 'Approved'),
		(4, 'Denied'),
		(5, 'Paid'),
		(6, 'Archived'),
	)
	value = models.IntegerField(choices=STATUS)
	date = models.DateTimeField(editable=False, default=timezone.now)
	author = models.ForeignKey(User, related_name="status_updates")
	document = models.ForeignKey(Document, related_name="status_updates")
	# purchase_order = models.ForeignKey(PurchaseOrder, related_name="status_updates", blank=True, null=True)
	# invoice = models.ForeignKey(Invoice, related_name="status_updates", blank=True, null=True)

	def __unicode__(self):
		return "Document {} [{}]".format(self.author, self.date)

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

