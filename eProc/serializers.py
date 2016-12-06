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