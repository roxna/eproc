from django.contrib import admin
from eProc.models import *

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    # fieldsets = [('Basic Info', {'fields': ['driver', 'passenger']}),
    #              ('Ride Details', {'fields': ['departure_city', 'arrival_city', 'departure_date', 'departure_time',
    #                                           'price_per_seat', 'num_seats_available']}),
    #              ('Ride restrictions', {'fields': ['no_smoking', 'no_pets', 'ladies_only']})]
    # search_fields = ['departure_city', 'arrival_city']
    # list_filter = ['driver', 'departure_date']
    list_display = ['username', 'email']



admin.site.register(User, UserAdmin)
admin.site.register(BuyerProfile)
admin.site.register(VendorProfile)
admin.site.register(AccountCode)
admin.site.register(CatalogItem)
admin.site.register(Category)
admin.site.register(OrderItem)
admin.site.register(Company)
admin.site.register(BuyerCo)
admin.site.register(VendorCo)
admin.site.register(Department)
admin.site.register(Location)
admin.site.register(Requisition)
admin.site.register(PurchaseOrder)
admin.site.register(Invoice)
admin.site.register(Rating)
admin.site.register(Status)
admin.site.register(Tax)
