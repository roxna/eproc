from django.contrib import admin
from eProc.models import *

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    # fieldsets = [('Basic Info', {'fields': ['driver', 'passenger']}),
    #              ('Ride Details', {'fields': ['departure_city', 'arrival_city', 'departure_date', 'departure_time',
    #                                           'price_per_seat', 'num_seats_available']}),
    #              ('Ride restrictions', {'fields': ['no_smoking', 'no_pets', 'ladies_only']})]
    list_display = ['id', 'username', 'first_name', 'last_name', 'email']

class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'department', 'company', 'approval_threshold']
    list_filter = ['company', 'role']

class RequisitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'current_status', 'department', 'buyer_co', ]
    search_fields = ['number', 'department']
    list_filter = ['number',]

class POAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'current_status', 'buyer_co', 'vendor_co', 'get_ordered_grandtotal']
    search_fields = ['number', 'department']
    list_filter = ['number', ]

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'current_status', 'buyer_co', 'vendor_co', 'get_grand_total']

class DrawdownAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'current_status', 'buyer_co' ]

class CatalogItemAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'item_type', 'unit_price', 'min_threshold', 'max_threshold', 'category', 'vendor_co']

class CatalogItemRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'unit_price', 'category']    

class CategoryAdmin(admin.ModelAdmin):
	list_display = ['id', 'code', 'name']	

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'product', 'qty_requested', 'qty_ordered','qty_approved', 'qty_delivered', 'current_status', 'get_latest_status']
    search_fields = ['product',  ]
    list_filter = ['product', 'requisition', 'purchase_order', 'invoice']

class DrawdownItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'product', 'qty_requested', 'qty_approved', 'current_status', 'get_latest_status']
    search_fields = ['product',  ]
    list_filter = ['product', 'drawdown']

class CompanyAdmin(admin.ModelAdmin):
	list_display = ['id', 'name']
    
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'location']

class AccountCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name']    

class SpendAllocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'department', 'account_code', 'spend']

class DocumentStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'value', 'date', 'author', 'document']
    list_filter = ['document']

class OrderItemStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'value', 'date', 'author', 'item',]    
    list_filter = ['value', 'item__product', 'item__product__buyer_cos', ]   

class DrawdownItemStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'value', 'date', 'author', 'item',]    
    list_filter = ['value', 'item__product', 'item__product__buyer_cos', ]  

class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'loc_type', 'company']  
    list_filter = ['company',]

class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'file', 'document']  

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'category']

class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'commodity', 'alert_price']

class CommodityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

admin.site.register(User, UserAdmin)
admin.site.register(BuyerProfile, BuyerProfileAdmin)
admin.site.register(AccountCode, AccountCodeAdmin)
admin.site.register(CatalogItem, CatalogItemAdmin)
admin.site.register(CatalogItemRequest, CatalogItemRequestAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(DrawdownItem, DrawdownItemAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(BuyerCo, CompanyAdmin)
admin.site.register(VendorCo, CompanyAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Document)
admin.site.register(Requisition, RequisitionAdmin)
admin.site.register(PurchaseOrder, POAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Drawdown, DrawdownAdmin)
admin.site.register(SpendAllocation, SpendAllocationAdmin)
admin.site.register(Rating)
admin.site.register(DocumentStatus, DocumentStatusAdmin)
admin.site.register(OrderItemStatus, OrderItemStatusAdmin)
admin.site.register(DrawdownItemStatus, DrawdownItemStatusAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Tax)
admin.site.register(PriceAlert, PriceAlertAdmin)
admin.site.register(Commodity, CommodityAdmin)