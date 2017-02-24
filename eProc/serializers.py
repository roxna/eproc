# SERIALIZERS the data for easy access in json format
# Read more: http://www.django-rest-framework.org/api-guide/serializers/#serializers
from rest_framework import serializers
from eProc.models import OrderItem


# Adds product name & price into order_item serialized data
# Used in new_invoice --> calls ajax 'po_orderitems' or /purchase-order/items/<po_id>/ in custom.js
class POItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ('product','qty_requested', 'comments_requested', 'price_requested', )   

# Used in 'unbilled_items_by_vendor' to update 'new_invoice_items' list
class UnbilledItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name")
    currency = serializers.CharField(source="product.currency")
    purchase_order = serializers.CharField(source="purchase_order.number")

    vendor_co = serializers.CharField(source="purchase_order.vendor_co")
    # get_delivered_statuses = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'currency', 'qty_delivered', 'comments_requested', 'price_ordered', 'purchase_order', 'vendor_co', 'get_delivered_subtotal' )
