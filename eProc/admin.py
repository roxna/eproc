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
    list_display = ['id', 'role', 'department', 'company']
    search_fields = ['company']

class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'company']
    list_filter = ['company']

class RequisitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'department', 'buyer_co', 'sub_total']
    search_fields = ['number', 'department']
    list_filter = ['number', 'sub_total']

class POAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'buyer_co', 'vendor_co', 'grand_total']
    # search_fields = ['number', 'department']
    # list_filter = ['number', 'sub_total']

class CatalogItemAdmin(admin.ModelAdmin):
	list_display = ['name', 'unit_price', 'category']

class CategoryAdmin(admin.ModelAdmin):
	list_display = ['code', 'name']	

class OrderItemAdmin(admin.ModelAdmin):
	list_display = ['product', 'quantity', 'unit_price']	

class CompanyAdmin(admin.ModelAdmin):
	list_display = ['id', 'name']
    
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'company']

class AccountCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name']    

class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'value', 'date', 'author', 'document']    

admin.site.register(User, UserAdmin)
admin.site.register(BuyerProfile, BuyerProfileAdmin)
admin.site.register(VendorProfile, VendorProfileAdmin)
admin.site.register(AccountCode, AccountCodeAdmin)
admin.site.register(CatalogItem, CatalogItemAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(BuyerCo, CompanyAdmin)
admin.site.register(VendorCo, CompanyAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Location)
admin.site.register(Document)
admin.site.register(Requisition, RequisitionAdmin)
admin.site.register(PurchaseOrder, POAdmin)
admin.site.register(Invoice)
admin.site.register(Rating)
admin.site.register(Status, StatusAdmin)
admin.site.register(Tax)