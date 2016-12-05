# SERIALIZERS the data for easy access in json format
# Read more: http://www.django-rest-framework.org/api-guide/serializers/#serializers

from rest_framework import serializers
from eProc.models import *


# Adds product name & price into order_item serialized data
# Used in new_invoice --> calls ajax 'po_orderitems' or /purchase-order/items/<po_id>/ in custom.js
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ('product','quantity', 'comments', 'unit_price', 'sub_total', )

class LocationSerializer(serializers.ModelSerializer):
    co_name = serializers.CharField(source="company.name")
    co_website = serializers.CharField(source="company.website")
    co_contact_rep = serializers.CharField(source="company.contact_rep")
    co_vendorID = serializers.CharField(source="vendorCo.vendorID")
    co_comments = serializers.CharField(source="vendorCo.comments")

    class Meta:
        model = Location
        fields = ('co_name', 'co_website', 'co_contact_rep','co_vendorID', 'co_comments',)

class VendorCoSerializer(serializers.ModelSerializer):
    # address1 = serializers.CharField(source="locations.address1")    

    class Meta:
        model = VendorCo
        fields = ('name', 'website', 'contact_rep','vendorID', 'comments', 
        		)


    	# var location = data[2]['fields'];
    	# $('#vendorEmail').text(location['email']);
    	# $('#vendorPhone').text(location['phone']);
    	# $('#vendorFax').text(location['fax']);
    	# $('#vendorAdd1').text(location['address1']);
    	# $('#vendorAdd2').text(location['address2']);
    	# $('#vendorCity').text(location['city']);
    	# $('#vendorState').text(location['state'].toUpperCase());
    	# $('#vendorZip').text(location['zipcode']);
    	# $('#vendorCountry').text(location['country'].toUpperCase());      