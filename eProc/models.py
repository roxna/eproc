from __future__ import unicode_literals
from datetime import date, timedelta
from decimal import DecimalException
from django.db import models
from django.db.models import Avg, Sum
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.validators import RegexValidator, MinValueValidator
from django.template.defaultfilters import slugify
from django.utils import timezone
from collections import defaultdict
from .managers import *
from .validators import validate_file_extension

################################
###      PAYMENT / SALE      ### 
################################ 

class Subscription(models.Model):
    charge_id = models.CharField(max_length=32)  #Stripe charge_id
    plan = models.ForeignKey('home.Plan', related_name='subscriptions') #FK to Plan Model in home app    

################################
###     COMPANY DETAILS     ### 
################################ 

# COMPANY - logos will be uploaded to <media_root>/<buyer_co_name>/logo/<filename>
def co_logo_directory_path(instance, filename):
	return '{0}/logo/{1}'.format(slugify(instance.name), filename)

class Company (models.Model):
	name = models.CharField(max_length=30)	
	industry = models.CharField(choices=settings.INDUSTRY_CHOICES, max_length=20, null=True, blank=True)
	currency = models.CharField(choices=settings.CURRENCIES, max_length=10, null=True, blank=True)
	website = models.CharField(max_length=100, null=True, blank=True)	
	logo = models.ImageField(upload_to=co_logo_directory_path, default='../static/img/default_logo.jpg', blank=True, null=True)

	def __unicode__(self):
		return "{}".format(self.name)

	def get_primary_location(self):
	    return self.locations.latest('id')

	def get_all_locations(self):
		return [location for location in self.locations.all()]

class BuyerCo(Company):
	is_subscribed = models.BooleanField(default=False)  #Is on trial_period or has subscribed
	subscription = models.OneToOneField(Subscription, related_name='buyer_co', null=True, blank=True)

	def is_trial_over(self):
		return timezone.now() > (self.users.first().user.date_joined + timedelta(days=settings.TRIAL_PERIOD_DAYS))

	def is_trial_over_not_subscribed(self):
		# Check if date SuperUser (registerer) was created was more than TRIAL_PERIOD_DAYS ago
		if not self.is_subscribed and self.is_trial_over():
			return True
		return False

	def days_to_trial_over(self):
		date_since_joined = (timezone.now().date() - self.users.first().user.date_joined.date()).days		
		# Once # days since joined > TRIAL_PERIOD_DAYS, shouldn't return a negative # days left
		return max(0, settings.TRIAL_PERIOD_DAYS - date_since_joined)

	def has_created_dept(self):
		for location in self.locations.all():
			if location.departments.all().exists():
				return True
		return False

class VendorCo(Company):
	contact_rep = models.CharField(max_length=150, default='-')
	vendorID = models.CharField(max_length=50, null=True, blank=True)
	bank_name = models.CharField(max_length=50, null=True, blank=True)
	branch_details = models.CharField(max_length=50, null=True, blank=True)
	ac_number = models.BigIntegerField(null=True, blank=True)
	company_number = models.CharField(max_length=20, null=True, blank=True)
	comments = models.CharField(max_length=150, null=True, blank=True)
	# M2M field if bulk_discount item; else FK
	buyer_cos = models.ManyToManyField(BuyerCo, related_name="vendor_cos", null=True, blank=True)

	def get_model_fields(model):
	    return model._meta.fields

	# Returns the value of the average rating (eg. Good/Bad..)
	def get_average_rating(self):
		# avg_score returns a tuple (#, rating) eg. (2, Average)		
		avg_score = int(self.ratings.all().aggregate(Avg('score'))['score__avg'])
		return dict(settings.SCORES)[avg_score]
		# return settings.SCORES[avg_score][1]

################################
###     LOCATION / DEPT      ### 
################################ 

class Location(models.Model):
	name = models.CharField(max_length=50, default='')
	loc_type = models.CharField(choices=settings.LOCATION_TYPES, max_length=20, default='HQ')	
	address1 = models.CharField(max_length=40, null=True, blank=True)
	address2 = models.CharField(max_length=40, null=True, blank=True)
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
		return u"{}".format(self.name)		

	def get_address(self):
		if self.address1 and self.city:
			return "{} {} \n {}, {} {}, {}".format(self.address1, self.address2, self.city, self.state, self.zipcode, self.country)
		else:
			return ""

	def get_num_users(self):
		return len(self.users.all())

	def get_num_depts(self):
		return len(self.departments.all())		

	def get_inventory_items(self):				
		# DefaultDict is like a regular dictionary but works better if key doesn't exist
		# items_list = { product_name: [qty_delivered, qty_drawndown, qty_inventory, min_thresh, max_thresh] }
		items_list = {}

		# INBOUND ORDER ITEMS
		order_items = OrderItem.objects.filter(requisition__department__location=self)
		for item in order_items:
			if item.current_status in settings.DELIVERED_STATUSES:
				try:
					items_list[item.product.name] = [
						items_list[item.product.name][0] + item.qty_delivered,
						items_list[item.product.name][1],						
						items_list[item.product.name][2] + item.qty_delivered, # inventory = current_inventory + qty_delivered
						item.product.min_threshold, 
						item.product.max_threshold, 
					]
				except KeyError:
					items_list[item.product.name] = [
						 item.qty_delivered,
						 0,
						 item.qty_delivered,
						 item.product.min_threshold,
						 item.product.max_threshold,
					]
		
		# OUTBOUND DRAWNDOWN ITEMS
		drawdown_items = DrawdownItem.objects.filter(drawdown__location=self)
		for item in drawdown_items:
			if item.current_status in settings.DRAWDOWN_STATUSES:
				try:
					items_list[item.product.name] = [
						items_list[item.product.name][0],
						items_list[item.product.name][1] - item.qty_drawndown,						
						items_list[item.product.name][2] - item.qty_drawndown, # inventory = current_inventory - qty_drawndown
						item.product.min_threshold, 
						item.product.max_threshold, 
					]
				except KeyError:
					items_list[item.product.name] = [
						 0,
						 item.qty_drawndown,
						 item.qty_drawndown,
						 item.product.min_threshold,
						 item.product.max_threshold,
					]

		return items_list
	

class Department(models.Model):
	name = models.CharField(max_length=50)
	budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	location = models.ForeignKey(Location, related_name='departments')

	def __unicode__(self):
		return "{}".format(self.name)

	# Total amount approved for spend or actually spent
	def get_spend_approved_ytd(self):
		spend = 0
		first_day_of_year = date(date.today().year, 1, 1)
		for requisition in self.requisitions.filter(status_updates__date__gte=first_day_of_year):
			spend += requisition.get_spend_approved_ytd()
		return spend

	def get_spend_percent_of_budget(self):
		try:
			percent = self.get_spend_approved_ytd()/self.budget*100
			return str(round(percent, 2)) + '%'
		except (ZeroDivisionError, DecimalException) as e:
			return "No budget defined"

################################
###   ACCOUNTING DETAILS     ### 
################################ 

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
	company = models.ForeignKey(BuyerCo, related_name='taxes')

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
    stripe_customer_id = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
    	return self.username

    def is_subscribed(self):
    	return self.buyer_profile.company.is_subscribed

    def is_trial_over(self):
    	return self.buyer_profile.company.is_trial_over()


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
	date_due = models.DateField(default=timezone.now)
	currency = models.CharField(choices=settings.CURRENCIES, default='USD', max_length=10)
	comments = models.CharField(max_length=100, null=True, blank=True)
	terms = models.CharField(max_length=5000, null=True, blank=True)
	preparer = models.ForeignKey(BuyerProfile, related_name="%(class)s_prepared_by")
	next_approver = models.ForeignKey(BuyerProfile, related_name="%(class)s_to_approve", null=True, blank=True)	
	buyer_co = models.ForeignKey(BuyerCo, related_name="%(class)s")
	current_status = models.CharField(max_length=25, choices=settings.DOC_STATUSES, default='Pending')
	
	def __unicode__(self):
		return "{}".format(self.number)

	# For docs, get_latest_status should be the same as get_current_status (OrderItems)
	# ...because all status updates are sequential
	def get_latest_status(self):
	    return self.status_updates.latest('date')

	def get_status_with_value(self, value):
		return self.status_updates.filter(value=value).order_by('-date')[0]

	def is_past_due(self):
		if timezone.now().date() > self.date_due:
			return True
		return False

	# Helper function for all get_x_subtotal functions
	def get_subtotal(self, price, quantity):
		subtotal = 0
		for item in self.items.all():
			try:
				#getattr allows you to access an attribute using a variable (i.e. item.price_req)
				subtotal += getattr(item, price) * getattr(item, quantity)  
			except TypeError: #If qty is not defined
				pass
		return subtotal

	# If doc is requested/denied/cancelled --> requested_subtotal
	def get_requested_subtotal(self):
		return self.get_subtotal('price_requested', 'qty_requested')
	def get_approved_subtotal(self):
		return self.get_subtotal('price_approved', 'qty_approved')	

class SalesOrder(Document):
	cost_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	cost_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	discount_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	tax_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	billing_add = models.ForeignKey(Location, related_name="%(class)s_billed", null=True, blank=True)
	shipping_add = models.ForeignKey(Location, related_name="%(class)s_shipped", null=True, blank=True)
	vendor_co = models.ForeignKey(VendorCo, related_name="%(class)s")
	is_paid = models.BooleanField(default=False)

 	class Meta:
 		abstract = True	


class Requisition(Document):
	department = models.ForeignKey(Department, related_name='requisitions')

	def get_spend_approved_ytd(self):
		spend = 0
		first_day_of_year = date(date.today().year, 1, 1)
		for item in self.items.filter(status_updates__date__gte=first_day_of_year):
			try:
				spend += item.get_approved_subtotal()
			except TypeError:
				pass
		return spend

class PurchaseOrder(SalesOrder):	
	pass

	def has_received_delivery(self):
		for item in self.items.all():
			if item.current_status in ['Delivered Complete', 'Delivered Partial']:
				return True
		return False

	def is_ready_to_close(self):
		for item in self.items.all():
			if item.current_status != 'Delivered Complete':
				return False
		return True

	# If doc is open/closed --> ordered_subtotal
	def get_ordered_subtotal(self):
		return self.get_subtotal('price_ordered', 'qty_ordered')

 	@property
 	def get_ordered_grandtotal(self):
 		return self.get_ordered_subtotal() + self.cost_shipping + self.cost_other + self.tax_amount - self.discount_amount

class Invoice(SalesOrder):
	date_issued = models.DateTimeField(default=timezone.now) #Date issued by the vendor
	purchase_orders = models.ManyToManyField(PurchaseOrder, related_name="invoices", null=True, blank=True)	

	def get_delivered_subtotal(self):
		return self.get_subtotal('price_ordered', 'qty_delivered')	

 	@property
 	def get_grand_total(self):
 		return self.get_delivered_subtotal() + self.cost_shipping + self.cost_other + self.tax_amount - self.discount_amount

# When goods returned, created by purchaser; credit note attached from vendor
class DebitNote(SalesOrder):
	invoices = models.ForeignKey(Invoice, related_name="debit_notes")

	def get_subtotal(self):
		subtotal = 0
		for item in self.items.all():
			try:
				subtotal += item.get_subtotal()
			except TypeError: #If qty is not defined
				pass
		return subtotal
	 	
 	def get_grandtotal(self):
 		return self.get_subtotal() + self.cost_shipping + self.cost_other + self.tax_amount - self.discount_amount


class Drawdown(Document):
	location = models.ForeignKey(Location, related_name='drawdowns')
	department = models.ForeignKey(Department, related_name='drawdowns')

	def is_ready_to_close(self):
		for item in self.items.all():
			if item.current_status != 'Drawndown Complete':
				return False
		return True

# Files uploaded to <media_root>/<buyer_co_name>/<doc_model_name>/<doc_number>/<filename>
# 		  		Eg: media/hattas-company/invoice/INV4/hatta.jpg  
def file_directory_path(instance, filename):	    
	return '{0}/{1}/{2}/{3}'.format(slugify(instance.document.buyer_co.name), instance.document.__class__.__name__, instance.document.number, filename)

class File(models.Model):
	name = models.CharField(max_length=50, blank=True, null=True)
	file = models.FileField(upload_to=file_directory_path, validators=[validate_file_extension]) #see validators.py
	comments = models.CharField(max_length=100, blank=True, null=True)
	document = models.ForeignKey(Document, related_name='files', blank=True, null=True)

	def __unicode__(self):
		return "{}".format(self.name)


##########################################
###    PRODUCT & ORDER LINE ITEMS      ### 
########################################## 

class Category(models.Model):
	code = models.IntegerField(null=True, blank=True)
	name = models.CharField(max_length=50)
	buyer_co = models.ForeignKey(BuyerCo, related_name="categories", null=True, blank=True) # No buyer_co if it's a bulk_discount category

	def __unicode__(self):
		return "{}".format(self.name)

# Images uploaded to <media_root>/... 
# To update path on whether it's 'Buyer Uploaded' or 'Bulk Discount'
def img_directory_path(instance, filename):    
	return 'catalog/images/{0}/{1}'.format(str(instance.id), filename)

# Parent model for CatalogItem/CatalogItemRequest models
class Product(models.Model):
	name = models.CharField(max_length=50)
	desc = models.CharField(max_length=150, null=True, blank=True)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)  #For CatalogItemRequest - it's max price buyer is willing to pay
	unit_type = models.CharField(max_length=20, default="each")
	currency = models.CharField(choices=settings.CURRENCIES, default='USD', max_length=10)
	category = models.ForeignKey(Category, related_name="%(class)ss")
	# M2M for bulk items, FK if not; No buyer_co if it's a bulk_discount category
	buyer_cos = models.ManyToManyField(BuyerCo, related_name="%(class)ss", null=True, blank=True) 

	class Meta:
 		abstract = True

 	@property
	def image_url(self):
	    if self.image and hasattr(self.image, 'url'):
	        return self.image.url
	    else:
	    	return static('dist/img/product_bulk_icon.jpg')

# An actual item in the catalog (either Buyer_Uploaded or Bulk_Discount)
class CatalogItem(Product):
	sku = models.CharField(max_length=20, null=True, blank=True)
	image = models.ImageField(upload_to=img_directory_path, validators=[validate_file_extension], null=True, blank=True)
	ITEM_TYPES = (
		('Buyer Uploaded', 'Buyer Uploaded'), 
		('Bulk Discount', 'Bulk Discount'), 
	)
	item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='Buyer Uploaded')	
	min_threshold = models.IntegerField(null=True, blank=True) # Alert if inventory drops below		
	max_threshold = models.IntegerField(null=True, blank=True) # Alert if inventory is higher than
	vendor_co = models.ForeignKey(VendorCo, related_name="catalogitems")

	def __unicode__(self):
		return "{}".format(self.name)

# Model that saves product requests from buyer_cos
class CatalogItemRequest(Product):
	author = models.ForeignKey(BuyerProfile, related_name="catalogitemrequests")

	def __unicode__(self):
		return "{}".format(self.name)

class DebitNoteItem(models.Model):
	desc = models.CharField(max_length=150)
	quantity = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	debit_note = models.ForeignKey(DebitNote, related_name="items")

	def __unicode__(self):
		return "{}".format(self.desc)

	def get_subtotal(self):
		try:
			return self.unit_price * self.quantity
		except TypeError: #If qty is not defined
			return 0

class Item(models.Model):
	number = models.CharField(max_length=20)
	product = models.ForeignKey(CatalogItem, related_name='%(class)ss')
	qty_requested = models.IntegerField(validators=[MinValueValidator(0)], )
	qty_approved = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
	qty_denied = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
	qty_cancelled = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
	comments_requested = models.CharField(max_length=500, blank=True, null=True)
	comments_approved = models.CharField(max_length=500, blank=True, null=True)
	date_due = models.DateField(default=timezone.now)
	current_status = models.CharField(max_length=25, choices=settings.CURRENT_STATUSES, default='Pending')

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
	price_requested = models.DecimalField(max_digits=10, decimal_places=2)
	price_approved = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	price_ordered = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	qty_ordered = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
	qty_delivered = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
	qty_returned = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
	comments_ordered = models.CharField(max_length=500, blank=True, null=True)	
	comments_delivered = models.CharField(max_length=500, blank=True, null=True)
	department = models.ForeignKey(Department, related_name="items")  #Dept that requested the item	
	requisition = models.ForeignKey(Requisition, related_name='items', null=True, blank=True)
	purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', null=True, blank=True)  #Assuming 1 item has 1PO for now
	invoice = models.ForeignKey(Invoice, related_name='items', null=True, blank=True)
	
	def __unicode__(self):
		return "[{}] {}".format(self.number, self.product.name)

	def is_invoiced(self):
		return self.invoice is not None

	def is_paid(self):
		return self.invoice.is_paid		

	# Helper function for all get_x_subtotal functions
	def get_subtotal(self, price, quantity):
		try:
			return price * quantity
		except TypeError: #If qty is not defined
			return '-'
	
	def get_requested_subtotal(self):
		return self.get_subtotal(self.price_requested, self.qty_requested)
	def get_approved_subtotal(self):
		return self.get_subtotal(self.price_approved, self.qty_approved)
	def get_ordered_subtotal(self):
		return self.get_subtotal(self.price_ordered, self.qty_ordered)
	def get_delivered_subtotal(self):
		return self.get_subtotal(self.price_ordered, self.qty_delivered)
	def get_returned_subtotal(self):
		return self.get_subtotal(self.price_ordered, self.qty_returned)

	def get_delivered_statuses(self):
	    return self.status_updates.filter(value__in=['Delivered'])
	
class DrawdownItem(Item):
	qty_drawndown = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True,)
	comments_drawdown = models.CharField(max_length=500, blank=True, null=True)
	drawdown = models.ForeignKey(Drawdown, related_name='items', null=True, blank=True)	

	def get_drawdown_statuses(self):
	    return self.status_updates.filter(value__in=['Drawndown'])

# Model to break down spend (DELIVERED_SUBTOTAL) of items between departments
class SpendAllocation(models.Model):
	item = models.ForeignKey(OrderItem, related_name="spend_by_dept")
	department = models.ForeignKey(Department, related_name="spend_allocation")
	account_code = models.ForeignKey(AccountCode, related_name="spend_allocation")
	spend = models.DecimalField(max_digits=10, decimal_places=2)

	def __unicode__(self):
		return "{} - {} spend of item {}".format(self.department.name, self.spend, self.item.number)	

##########################################
#####      STATUS (DOC & ITEM)       ##### 
########################################## 

class StatusLog(models.Model):
	value = models.CharField(max_length=40, choices=settings.ITEM_STATUSES, default='Pending')
	desc = models.CharField(max_length=100, null=True, blank=True)
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

class DocumentStatus(StatusLog):
	document = models.ForeignKey(Document, related_name="status_updates")

	# Override the choices for DocumentStatus 'value' field
	def __init__(self, *args, **kwargs):
		self._meta.get_field('value').choices=settings.DOC_STATUSES
		super(DocumentStatus, self).__init__(*args, **kwargs)

class OrderItemStatus(StatusLog):
	item = models.ForeignKey(OrderItem, related_name='status_updates')

class DrawdownItemStatus(StatusLog):
	item = models.ForeignKey(DrawdownItem, related_name='status_updates')

##########################################
#####    RATINGS & NOTIFICATIONS     ##### 
########################################## 

class Rating(models.Model):	
	score = models.IntegerField(choices=settings.SCORES)
	category = models.CharField(choices=settings.CATEGORIES, max_length=15, default='Total')
	rater = models.ForeignKey(User, related_name="ratings")
	vendor_co = models.ForeignKey(VendorCo, related_name="ratings")
	comments = models.CharField(max_length=100)

	def __unicode__(self):
		return u"{} - {}".format(self.vendor_co, self.score)

class Notification(models.Model):
	"""
    Significantly simplified version of django-notifications
    Details: https://github.com/django-notifications/django-notifications/blob/master/notifications/models.py
    Haven't implemented "Action model describing the actor acting out a verb (on an optional target)"
    	<actor> <verb> <action_object> <target> <time> 
    Instead, simple text string notification for now
    """
	text = models.CharField(max_length=100, blank=False)
	CATEGORIES = (		
		('Info', 'Info'),
		('Success', 'Success'),
		('Warning', 'Warning'),
		('Error', 'Error')
	)
	category = models.CharField(choices=CATEGORIES, default='Info', max_length=20)
	recipients = models.ManyToManyField(User, null=True, blank=True, related_name='notifications') #null=True because need to save M2M field
	is_unread = models.BooleanField(default=True, blank=False)
	target = models.CharField(max_length=100, null=True, blank=True) #url

	def __unicode__(self):
		return u"{}".format(self.text)

	def mark_as_read(self):
		if self.is_unread:
			self.is_unread = False
			self.save()

##########################################
#####         PRICE ALERTS           ##### 
########################################## 

class Commodity(models.Model):
	name = models.CharField(choices=settings.COMMODITIES, max_length=100, blank=False)
	# The API KeyCode from Quandl https://www.quandl.com/collections/markets/commodities
	api_key_code = models.CharField(max_length=20, )
	unit = models.CharField(max_length=10, default='$/mt')

	def __unicode__(self):
		return u"{} ({})".format(self.name, self.unit)

	@classmethod
	def get_current_price(self):
		url = "https://www.quandl.com/api/v3/datasets/{1}.json?api_key={2}".format(self.api_key_code, settings.QUANDL_API_KEY)
		response_dict = requests.get(url).json()
		return jsonify(response_dict)


class PriceAlert(models.Model):
	commodity = models.ForeignKey(Commodity, related_name="price_alerts")
	alert_price = models.DecimalField(max_digits=10, decimal_places=2)	
	is_active = models.BooleanField(default=True)
	buyer_co = models.ForeignKey(BuyerCo, related_name="price_alerts")	
	author = models.ForeignKey(BuyerProfile, related_name="price_alerts")

	def __unicode__(self):
		return u"{} for {}".format(self.alert_price, self.commodity)

    

    


