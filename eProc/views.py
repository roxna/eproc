from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login as auth_login
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.forms import UserChangeForm
from django.core.serializers import serialize
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Sum, Max, Avg, F, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import inlineformset_factory,BaseModelFormSet, modelformset_factory
from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.template.response import TemplateResponse
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.urls import reverse
from django.utils import timezone
from django.utils.http import is_safe_url
from datetime import datetime, timedelta
from rest_framework.renderers import JSONRenderer
from eProc.models import *
from eProc.serializers import *
from eProc.forms import *
from eProc.utils import *
from itertools import chain
from collections import defaultdict
import csv
import pdb


####################################
###         REGISTRATION         ### 
####################################

def register(request):
    user_form = RegisterUserForm(request.POST or None)  
    buyer_company_form = BuyerCoForm(request.POST or None)      
    if request.method == "POST":
        if  user_form.is_valid() and buyer_company_form.is_valid():
            user_instance = user_form.save()
            company = buyer_company_form.save()
            location = Location.objects.create(loc_type='HQ', name=company.name+' - HQ', company=company)
            department = Department.objects.create(name='Admin', location=location)
            buyer_profile = BuyerProfile.objects.create(role='SuperUser', user=user_instance, department=department, company=company)
            messages.info(request, "Thank you for registering. You are now logged in.")
            user = authenticate(username=user_form.cleaned_data['username'],password=user_form.cleaned_data['password1'])
            user.is_active=False #User not active until activate account through email
            user.save()
            send_verific_email(user, user.id*settings.SCALAR)
            return redirect('thankyou')
        else:
            messages.error(request, 'Error. Registration unsuccessful') #TODO: Figure out how to show errors
    data = {
        'user_form': user_form,
        'buyer_company_form': buyer_company_form
    }
    return render(request, "registration/register.html", data)

def activate(request):
    user_id = int(request.GET.get('id'))/settings.SCALAR
    try:
        user = User.objects.get(id=user_id)
        user.is_active=True
        user.save()
    except:
        pass
    return render(request,'registration/activate.html')

def thankyou(request):
    return render(request, 'registration/thankyou.html')

####################################
###         MAIN PAGES           ### 
####################################

@login_required()
def get_started(request):
    buyer = request.user.buyer_profile
    req_exists = Requisition.objects.filter(buyer_co=buyer.company).exists()
    po_exists = PurchaseOrder.objects.filter(buyer_co=buyer.company).exists()
    invoice_exists = Invoice.objects.filter(buyer_co=buyer.company).exists()
    dd_exists = Drawdown.objects.filter(buyer_co=buyer.company).exists()
    data = {        
        'settings_list': [
            # url (name), text_to_display, action_completed?
            ['locations','1. Add locations & departments', Location.objects.filter(company=buyer.company).exists()],
            ['vendors','2. Add vendors', VendorCo.objects.filter(buyer_co=buyer.company).exists()],
            ['categories','3. Create product categories', Category.objects.filter(buyer_co=buyer.company).exists()],
            ['products','4. Upload product catalog', CatalogItem.objects.filter(buyer_co=buyer.company).exists()],
            ['account_codes','4. Create account codes', AccountCode.objects.filter(company=buyer.company).exists()],
            ['approval_routing','5. Set up approval routing', BuyerProfile.objects.filter(company=buyer.company, approval_threshold__gte=100).exists()],
            ['users','6. Add / view users', BuyerProfile.objects.filter(company=buyer.company).exclude(user=request.user).exists()],
            
        ],
        'request_list': [
            ['new_requisition','1. Create a new request', req_exists],
            ['requisitions','2. Approve/decline requests', req_exists],
        ],
        'procure_list': [
            ['new_po_items','1. Create a purchase order', po_exists],
            ['purchaseorders','2. View open/pending POs', po_exists],
        ],
        'pay_list': [
            ['new_invoice','1. Track invoices', invoice_exists],
            ['receive_pos','2. Receive items', dd_exists],
            ['new_drawdown','3. Create drawdowns', dd_exists],
            ['inventory','4. Track inventory', dd_exists],
        ],               
    }
    return render(request, "main/get_started.html", data)

@login_required()
def dashboard(request):
    buyer = request.user.buyer_profile
    
    # Only show documents where user is preparer or next_approver (unless SuperUser)
    requisitions = get_documents_by_auth(buyer, Requisition)
    pos = get_documents_by_auth(buyer, PurchaseOrder)

    all_requisitions, pending_requisitions, open_requisitions, approved_requisitions, closed_requisitions, paid_requisitions, cancelled_requisitions, denied_requisitions = get_documents_by_status(buyer, requisitions)
    all_pos, pending_pos, open_pos, approved_pos, closed_pos, paid_pos, cancelled_pos, denied_pos = get_documents_by_status(buyer, pos)    
    
    # Order Items with latest_status = 'Delivered PARTIAL/COMLPETE' (see managers.py) in the requester's department (in the past 7 days)
    items_received = OrderItem.latest_status_objects.delivered.filter(requisition__department=buyer.department)
    items_received = items_received.filter(latest_update__gte=datetime.now()-timedelta(days=7))

    data = {
        'pending_requisitions': pending_requisitions,
        'pending_pos': pending_pos,
        'items_received': items_received,
    }
    return render(request, "main/dashboard.html", data)

import unicodedata
from random import randint
@login_required()
def analysis(request):
    buyer = request.user.buyer_profile
    
    # Order Items with latest_status = 'Delivered PARTIAL/COMLPETE' (see managers.py) in the requester's department
    items_received = OrderItem.latest_status_objects.delivered.filter(requisition__department=buyer.department)

    location_spend = items_received.values('invoice__shipping_add__name').annotate(total_cost=Sum(F('qty_ordered')*F('unit_price'), output_field=models.DecimalField()))
    categ_spend = items_received.values('product__category__name').annotate(total_cost=Sum(F('qty_ordered')*F('unit_price'), output_field=models.DecimalField()))
    product_spend = items_received.values('product__name').annotate(total_cost=Sum(F('qty_ordered')*F('unit_price'), output_field=models.DecimalField()))
    supplier_spend = items_received.values('product__vendor_co__name').annotate(total_cost=Sum(F('qty_ordered')*F('unit_price'), output_field=models.DecimalField()))

    data = {
        'location_spend': location_spend,        
        'categ_spend': categ_spend,
        'product_spend': product_spend,
        'supplier_spend': supplier_spend,
    }    
    return render(request, "main/analysis.html", data)

####################################
###        REQUISITIONS          ### 
####################################

@login_required
def new_requisition(request): 
    buyer = request.user.buyer_profile
    requisition_form = RequisitionForm(request.POST or None,
                                       initial= {'number': "RO"+str(Requisition.objects.filter(buyer_co=buyer.company).count()+1)})        
    OrderItemFormset = inlineformset_factory(parent_model=Requisition, model=NewReqItemForm, form=OrderItemForm, extra=1)
    orderitem_formset = OrderItemFormset(request.POST or None)
    initialize_req_form(buyer, requisition_form, orderitem_formset)
    
    if request.method == "POST":
        if requisition_form.is_valid() and orderitem_formset.is_valid():
            requisition = save_new_document(buyer, requisition_form)
            # Save order_items and statuses (Req & Order Item status) --> see utils.py
            save_items(buyer, requisition, orderitem_formset)
            if buyer.role == 'SuperUser':
                save_status(document=requisition, doc_status='Approved', item_status='Approved', author=buyer)
            else:
                save_status(document=requisition, doc_status='Pending', item_status='Requested', author=buyer)
            messages.success(request, 'Requisition submitted successfully')
            return redirect('requisitions')
        else:
            messages.error(request, 'Error. Requisition not submitted')
    data = {
        'requisition_form': requisition_form,
        'orderitem_formset': orderitem_formset,
        'table_headers': ['Product', 'Quantity', 'Account Code', 'Comments'],
    }
    return render(request, "requests/new_requisition.html", data)

# Get relevant product and serialize the data into json for ajax request
@login_required
def product_details(request, product_id):
    product = get_object_or_404(CatalogItem, pk=product_id)    
    return HttpResponse(serialize('json', [product,]), content_type='application/json')

@login_required()
def requisitions(request):
    buyer = request.user.buyer_profile
    
    # Returns Reqs where the user is either the preparer OR next_approver, unless user is SuperUser (see utils.py)
    requisitions = get_documents_by_auth(buyer, Requisition)
    
    # Returns relevant requisitions based on their latest_status (see managers.py)    
    data = {
        'all_requisitions': Requisition.latest_status_objects.filter(pk__in=requisitions),
        'pending_requisitions': Requisition.latest_status_objects.pending.filter(pk__in=requisitions),
        'approved_requisitions': Requisition.latest_status_objects.approved.filter(pk__in=requisitions),
        'denied_requisitions': Requisition.latest_status_objects.denied.filter(pk__in=requisitions),
        'cancelled_requisitions': Requisition.latest_status_objects.cancelled.filter(pk__in=requisitions),
    }
    return render(request, "requests/requisitions.html", data)

@login_required
def view_requisition(request, requisition_id):
    buyer = request.user.buyer_profile
    requisition = get_object_or_404(Requisition, pk=requisition_id)    
    # Manage approving/denying requisitions (see utils.py)
    if request.method == 'POST':
        if 'approve' in request.POST:
            save_status(document=requisition, doc_status='Approved', item_status='Approved', author=buyer)
            messages.success(request, 'Requisition approved')
        elif 'deny' in request.POST:
            save_status(document=requisition, doc_status='Denied', item_status='Denied', author=buyer)
            messages.success(request, 'Requisition denied')
        elif 'cancel' in request.POST:
            save_status(document=requisition, doc_status='Cancelled', item_status='Cancelled', author=buyer)
            messages.success(request, 'Requisition Cancelled')          
        else:
            messages.error(request, 'Error. Requisition not updated')
        return redirect('requisitions')
    data = {
        'requisition': requisition,
        'table_headers': ['Product', 'Quantity', 'Account Code', 'Comments'],
    }
    return render(request, "requests/view_requisition.html", data)

@login_required
def print_requisition(request, requisition_id):
    requisition = get_object_or_404(Requisition, pk=requisition_id)
    data = {
        'requisition': requisition,        
    }
    return render(request, "requests/print_requisition.html", data)

####################################
###      PURCHASE ORDERS         ### 
####################################

@login_required
def new_po_items(request):
    buyer = request.user.buyer_profile
    
    # Get list of Order Items with latest_status = 'Approved' from the company, where the PO hasn't already been allocated
    approved_order_items = OrderItem.latest_status_objects.approved.filter(requisition__buyer_co=buyer.company).exclude(purchase_order__isnull=False)
        
    if request.method == 'POST':
        # Get items selected and convert to comma-separated string
        items = request.POST.getlist('order_items')
        item_ids = ','.join(items)
        
        # Redirect to new_po_confirm with query parameters = ids of items
        redirect_url = reverse('new_po_confirm')
        query_params = '?item_ids=' + str(item_ids)
        return HttpResponseRedirect (redirect_url + query_params)

    currency = buyer.company.currency
    data = {
        'approved_order_items': approved_order_items,
        'currency': currency,
        'table_headers': ['', 'Order No.', 'Item', 'Vendor', 'Required', 'Cost ('+currency+')'],        
    }
    return render(request, "pos/new_po_items.html", data)

@login_required
def new_po_confirm(request):    
    buyer = request.user.buyer_profile

    # Get the items selected in new_po_items from the query parameter
    item_ids = request.GET.get('item_ids')
    item_id_array = item_ids.split(",")
    items = OrderItem.objects.filter(id__in=item_id_array)

    # PO Order Items Formset with editable unit_price
    NewPOItemFormSet = modelformset_factory(model=OrderItem, form=NewPOItemForm, extra=0)
    po_items_formset = NewPOItemFormSet(request.POST or None, queryset=items)

    # PO Form
    po_form = PurchaseOrderForm(request.POST or None,
                                initial= {'number': "PO"+str(PurchaseOrder.objects.filter(buyer_co=buyer.company).count()+1)})
    initialize_po_form(buyer, po_form)
    
    if request.method == 'POST':
        if po_form.is_valid() and po_items_formset.is_valid():
            purchase_order = save_new_document(buyer, po_form)
            save_doc_status(document=purchase_order, value='Open', author=buyer)

            for orderitem_form in po_items_formset.forms:
                if orderitem_form.is_valid():
                    item = orderitem_form.save(commit=False)
                    item.purchase_order = purchase_order
                    item.save()
                    
                    purchase_order.sub_total += item.get_approved_subtotal
                    OrderItemStatus.objects.create(value='Ordered', author=buyer, order_item=item)

                    # Create a new Order Item with the same details (Item#, Req# etc) as current
                    # However, qty_requested = items that were approved but weren't ordered
                    approved_not_ordered = item.qty_approved - item.qty_ordered
                    if approved_not_ordered > 0:
                        approved_not_ordered_item = OrderItem.objects.create(number=item.number, qty_requested=item.qty_requested, qty_approved=approved_not_ordered, unit_price=item.product.unit_price, date_due=item.date_due, account_code=item.account_code, product=item.product, requisition=item.requisition)            
                        OrderItemStatus.objects.create(value='Approved', author=item.requisition.get_status_with_value('Approved').get_author(), order_item=approved_not_ordered_item)

                    
            purchase_order.grand_total = purchase_order.sub_total + purchase_order.cost_shipping + purchase_order.cost_other + purchase_order.tax_amount - purchase_order.discount_amount
            purchase_order.save()
            messages.success(request, 'PO created successfully')
            return redirect('purchaseorders')
        else:
            messages.error(request, 'Error. Purchase order not created')
    
    currency = buyer.company.currency
    data = {
        'po_form': po_form,
        'po_items_formset': po_items_formset,
        'currency': currency,
    }
    return render(request, "pos/new_po_confirm.html", data)

@login_required
def purchaseorders(request):
    buyer = request.user.buyer_profile
    
    # Not using get_documents_by_auth function because assume purchasing is a centralized (not location-based) function
    pos = PurchaseOrder.objects.filter(buyer_co=buyer.company)
    
    data = {
        'all_pos': PurchaseOrder.latest_status_objects.filter(pk__in=pos),
        'open_pos': PurchaseOrder.latest_status_objects.open.filter(pk__in=pos),
        'closed_pos': PurchaseOrder.latest_status_objects.closed.filter(pk__in=pos),
        'paid_pos': PurchaseOrder.latest_status_objects.paid.filter(pk__in=pos),
        'cancelled_pos': PurchaseOrder.latest_status_objects.cancelled.filter(pk__in=pos),
        'href': 'view_purchaseorder',
        'title': 'Purchase Orders',
    }
    return render(request, "pos/purchaseorders.html", data)

@login_required
def print_purchaseorder(request, po_id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
    data = {
        'purchase_order': purchase_order,        
    }
    return render(request, "pos/print_purchaseorder.html", data)

@login_required
def view_purchaseorder(request, po_id):
    buyer = request.user.buyer_profile
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            save_status(document=purchase_order, doc_status='Cancelled', item_status='Cancelled', author=buyer)
            messages.success(request, 'PO Cancelled')
            return redirect('purchaseorders')
        elif 'paid' in request.POST:
            save_status(document=purchase_order, doc_status='Paid', item_status='Paid', author=buyer)
            messages.success(request, 'PO marked as Paid') 
            return redirect('purchaseorders')
        else:
            messages.error(request, 'Error. PO not updated')
        
    data = {
        'purchase_order': purchase_order,
    }
    return render(request, "pos/view_purchaseorder.html", data)

@login_required
def receive_pos(request):
    buyer = request.user.buyer_profile
    pos = get_documents_by_auth(buyer, PurchaseOrder)
    all_pos, pending_pos, open_pos, approved_pos, closed_pos, paid_pos, cancelled_pos, denied_pos = get_documents_by_status(buyer, pos)
    data = {
        'open_pos': open_pos,
    }
    return render(request, "pos/receive_pos.html", data)

@login_required
def receive_purchaseorder(request, po_id):
    buyer = request.user.buyer_profile
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
    ReceivePOItemFormSet = inlineformset_factory(PurchaseOrder, OrderItem, ReceivePOItemForm, extra=0)
    receive_po_formset = ReceivePOItemFormSet(request.POST or None, instance=purchase_order)

    if request.method == 'POST':
        if 'close' in request.POST:
            DocumentStatus.objects.create(value='Closed', author=buyer, document=purchase_order)
            # No Order Item status updates needed because 'Close' only shows if doc.is_ready_to_close:
            # order item statuses should be uptodate i.e. qty_ordered = qty_delivered + qty_returned)
            messages.success(request, 'Purchase Order closed')
            return redirect('purchaseorders')
        elif 'save' in request.POST:
            for index, form in enumerate(receive_po_formset.forms):
                if form.is_valid() and form.has_changed():
                    qty_ordered = form.cleaned_data['qty_ordered']
                    qty_delivered = form.cleaned_data['qty_delivered']
                    qty_returned = form.cleaned_data['qty_returned']
                    if qty_delivered > qty_ordered:
                        messages.error(request, 'Error. Quantity delivered must be less than quantity ordered.')
                    elif qty_returned > qty_delivered:
                        messages.error(request, 'Error. Quantity returned must be less than quantity delivered.')
                    elif qty_returned > qty_ordered:
                        messages.error(request, 'Error. Quantity returned must be less than quantity ordered.')                        
                    elif qty_delivered + qty_returned == qty_ordered:
                        item = form.save()
                        OrderItemStatus.objects.create(value='Delivered Complete', author=buyer, order_item=item)
                        messages.success(request, 'Orders updated successfully')
                    else:
                        item = form.save()
                        OrderItemStatus.objects.create(value='Delivered Partial', author=buyer, order_item=item)
                        messages.success(request, 'Orders updated successfully')
            return redirect('receive_purchaseorder', purchase_order.pk)
        else:
            messages.error(request, 'Error updating items')            
    data = {
        'purchase_order': purchase_order,
        'receive_po_formset': receive_po_formset,
    }
    return render(request, "pos/receive_purchaseorder.html", data)

@login_required
def po_orderitems(request, po_id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
    buyer_co = request.user.buyer_profile.company
    try:
        # Get relevant PO orderItems and serialize the data into json for ajax request
        order_items = OrderItem.objects.filter(purchase_order=purchase_order)
        data = OrderItemSerializer(order_items, many=True).data
    except TypeError:
        data = []
    return HttpResponse(JSONRenderer().render(data), content_type='application/json')


####################################
###           INVOICES           ### 
####################################

@login_required
def new_invoice(request):
    buyer = request.user.buyer_profile
    currency = buyer.company.currency
    invoice_form = InvoiceForm(request.POST or None,
                                initial= {'number': "INV"+str(Invoice.objects.filter(buyer_co=buyer.company).count()+1)})    
    initialize_invoice_form(buyer, invoice_form)
    file_form = FileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        file_form = FileForm(request.POST, request.FILES)
        if invoice_form.is_valid() and file_form.is_valid():
            invoice = save_new_document(buyer, invoice_form)            
            purchase_order = invoice_form.cleaned_data['purchase_order']
            invoice.sub_total = purchase_order.sub_total
            invoice.grand_total = purchase_order.grand_total
            invoice.billing_add = purchase_order.billing_add
            invoice.shipping_add = purchase_order.shipping_add
            invoice.save()
            for order_item in purchase_order.order_items.all():
                order_item.invoice = invoice
                order_item.save()

            upload_file = file_form.save(commit=False)
            upload_file.name = request.FILES['file'].name
            upload_file.document = invoice
            upload_file.save()
            
            # TODO: Make Invoice "Open", Add Approval process to Invoices
            DocumentStatus.objects.create(value='Approved', author=buyer, document=invoice)
            DocumentStatus.objects.create(value='Paid', author=buyer, document=purchase_order)
            messages.success(request, 'Invoice created successfully')
            return redirect('invoices')  
        else:
            messages.error(request, 'Error. Invoice not created')    
    data = {
        'invoice_form': invoice_form,
        'file_form': file_form,
        'currency': currency,
    }
    return render(request, "invoices/new_invoice.html", data)

@login_required
def invoices(request):
    buyer = request.user.buyer_profile    
    
    # Returns Invoices where the user is either the preparer OR next_approver, unless user is SuperUser (see utils.py)
    invoices = get_documents_by_auth(buyer, Invoice)
    
    data = {
        'all_invoices': Invoice.latest_status_objects.filter(pk__in=invoices),
        'pending_invoices': Invoice.latest_status_objects.pending.filter(pk__in=invoices),
        'approved_invoices': Invoice.latest_status_objects.approved.filter(pk__in=invoices),
        'cancelled_invoices': Invoice.latest_status_objects.cancelled.filter(pk__in=invoices),
        'paid_invoices': Invoice.latest_status_objects.paid.filter(pk__in=invoices),
        'table_headers': ['Invoice No.', 'Amount ('+buyer.company.currency+')', 'Invoice Created', 'Date Due', 'Vendor', 'PO No.', 'File', 'Comments']
    }
    return render(request, "invoices/invoices.html", data)

@login_required
def print_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    data = {
        'invoice': invoice,        
    }
    return render(request, "invoices/print_invoice.html", data)

@login_required
def view_invoice(request, invoice_id):
    buyer = request.user.buyer_profile
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if request.method == 'POST':
        if 'paid' in request.POST:
            save_status(document=invoice, doc_status='Paid', item_status='Paid', author=buyer)
            messages.success(request, 'Invoice marked as Paid')
        else:
            messages.error(request, 'Error. Invoice not updated')
        return redirect('invoices')
    data = {
        'invoice': invoice,
    }
    return render(request, "invoices/view_invoice.html", data)

@login_required
def vendor_invoices(request, vendor_id):
    buyer_co = request.user.buyer_profile.company
    vendor_co = get_object_or_404(VendorCo, pk=vendor_id)    
    try:
        purchase_orders = PurchaseOrder.objects.filter(buyer_co=buyer_co, vendor_co=vendor_co)
        po_numbers = [order.number for order in purchase_orders]
        documents = Document.objects.filter(number__in=po_numbers)
        data = serialize('json', list(documents))
    except TypeError:
        pass
    return HttpResponse(data, content_type='application/json')


####################################
###          INVENTORY           ### 
####################################

@login_required
def inventory(request):    
    buyer = request.user.buyer_profile
    locations = Location.objects.filter(company=buyer.company)        
    data = {
        'locations': locations,
    }
    return render(request, "inventory/inventory.html", data)

@login_required
def view_location_inventory(request, location_id, location_name):
    buyer = request.user.buyer_profile
    location = get_object_or_404(Location, pk=location_id)
    all_items = OrderItem.objects.filter(invoice__shipping_add=location)    
    
    # _list: querylist with individual items // _count: aggregate sum of qty for item in querylist
    delivered_list, delivered_count = get_inventory_received(all_items) #(for inventory_delivered)
    drawndown_list, drawndown_count = get_inventory_drawndown(all_items) #(for inventory_drawdown)
    neg_drawndown_list, neg_drawndown_count = get_inventory_drawndown(all_items, -1) # Negate drawdown items (for inventory_current)
    
    # Chain/combine the two querysets into a list, not another Queryset (can't use annotate etc)
    # TypeError for empty list
    try:
        inventory_list = list(chain(delivered_count, neg_drawndown_count)) 
    except TypeError:
        inventory_list = []

    data = {
        'location': location,
        'inventory_list': inventory_list,
        'delivered_list': delivered_list,
        'drawndown_list': drawndown_list,
    }
    return render(request, "inventory/inventory_location.html", data)


####################################
###          DRAWDOWNS           ### 
####################################

@login_required
def new_drawdown(request):
    buyer = request.user.buyer_profile
    drawdown_form = DrawdownForm(request.POST or None,
                                       initial= {'number': 'DD'+str(Drawdown.objects.filter(buyer_co=buyer.company).count()+1)})
    DrawdownItemFormSet = inlineformset_factory(parent_model=Drawdown, model=OrderItem, form=DrawdownItemForm, extra=1)
    drawdownitem_formset = DrawdownItemFormSet(request.POST or None)
    initialize_drawdown_form(buyer, drawdown_form, drawdownitem_formset)    
    
    if request.method == "POST":
        if drawdown_form.is_valid() and drawdownitem_formset.is_valid():
            drawdown = save_new_document(buyer, drawdown_form)
            save_items(buyer, drawdown, drawdownitem_formset)
            if buyer.role == 'SuperUser':
                save_status(document=drawdown, doc_status='Approved', item_status='Drawdown Approved', author=buyer)
            else:
                save_status(document=drawdown, doc_status='Pending', item_status='Drawdown Requested', author=buyer)
            messages.success(request, 'Drawdown submitted successfully')
            return redirect('drawdowns')
        else:
            messages.error(request, 'Error. Drawdown not submitted')
    data = {
        'drawdown_form': drawdown_form,
        'drawdownitem_formset': drawdownitem_formset,
        'table_headers': ['Product', 'Quantity', 'Comments'],
    }
    return render(request, "inventory/new_drawdown.html", data)

@login_required
def view_drawdown(request, drawdown_id):
    buyer = request.user.buyer_profile
    drawdown = get_object_or_404(Drawdown, pk=drawdown_id)
    # pdb.set_trace()
    if request.method == 'POST':
        if 'approve' in request.POST:
            save_status(document=drawdown, doc_status='Approved', item_status='Drawdown Approved', author=buyer)
            messages.success(request, 'Drawdown Approved')
        elif 'deny' in request.POST:
            save_status(document=drawdown, doc_status='Denied', item_status='Drawdown Denied', author=buyer)            
            messages.success(request, 'Drawdown Denied')     
        elif 'cancel' in request.POST:
            save_status(document=drawdown, doc_status='Cancelled', item_status='Drawdown Cancelled', author=buyer)
            messages.success(request, 'Drawdown Cancelled')                        
        else:
            messages.error(request, 'Error. Drawdown not updated')
        return redirect('drawdowns')
    data = {
        'drawdown': drawdown,
    }
    return render(request, "inventory/view_drawdown.html", data)

@login_required
def print_drawdown(request, drawdown_id):
    drawdown = get_object_or_404(Drawdown, pk=drawdown_id)
    data = {
        'drawdown': drawdown,        
    }
    return render(request, "inventory/print_drawdown.html", data)

@login_required
def drawdowns(request):
    buyer = request.user.buyer_profile

    # Returns DDs where the user is either the preparer OR next_approver, unless user is SuperUser (see utils.py)
    drawdowns = get_documents_by_auth(buyer, Drawdown)

    data = {
        'all_drawdowns': Drawdown.latest_status_objects.filter(pk__in=drawdowns),
        'pending_drawdowns': Drawdown.latest_status_objects.pending.filter(pk__in=drawdowns),
        'approved_drawdowns': Drawdown.latest_status_objects.approved.filter(pk__in=drawdowns),
        'denied_drawdowns': Drawdown.latest_status_objects.denied.filter(pk__in=drawdowns),
        'cancelled_drawdowns': Drawdown.latest_status_objects.cancelled.filter(pk__in=drawdowns),
        'table_headers': ['Drawdown No.', 'Date Requested', 'Comments']
    }
    return render(request, "inventory/drawdowns.html", data)

####################################
###           SETTINGS           ### 
####################################

@login_required
def settings(request):
    return render(request, "settings/settings.html")

@login_required
def users(request):    
    buyer = request.user.buyer_profile
    # user_form = AddUserForm(request.POST or None)
    # buyer_profile_form = BuyerProfileForm(request.POST or None)
    # buyer_profile_form.fields['department'].queryset = Department.objects.filter(location__in=buyer.company.get_all_locations())
    # buyer_profile_form.fields['location'].queryset = Location.objects.filter(company=buyer.company)
    if request.method == "POST":
        # if 'add' in request.POST:
        #     if user_form.is_valid() and buyer_profile_form.is_valid():                
        #         user = user_form.save()
        #         buyer_profile = buyer_profile_form.save(commit=False)
        #         buyer_profile.user = user                
        #         buyer_profile.company = buyer.company
        #         buyer_profile.save()
        #         send_verific_email(user, user.id*settings.SCALAR)
        #         messages.success(request, 'User successfully invited')
        #         return redirect('users')
        #     else:
        #         messages.error(request, 'Error adding user. Please try again.')
        if 'delete' in request.POST:          
            for key in request.POST:
                if key == 'delete':
                    buyer_id = int(request.POST[key])
                    buyer_to_delete = BuyerProfile.objects.get(pk=buyer_id)
                    user_to_delete = User.objects.get(buyer_profile=buyer_to_delete)
                    if user_to_delete == request.user:
                        messages.error(request, 'Sorry, you can not delete yourself')
                    else:
                        user_to_delete.delete()
                        buyer_to_delete.delete()
                        messages.success(request, 'User ' + user_to_delete.username + ' successfully deleted')
                        return redirect('users')
        else:
            messages.error(request, 'Error. Please try again.')
            return redirect('users')
    buyers = BuyerProfile.objects.filter(company=buyer.company)
    data = {
        'buyers': buyers,
        # 'user_form': user_form,
        # 'buyer_profile_form': buyer_profile_form,
        'table_headers': ['Username', 'Email Address', 'Role', 'Location', 'Dept', 'Status', ' ',]
    }
    return render(request, "settings/users.html", data)

@login_required
def locations(request):
    buyer = request.user.buyer_profile
    locations = Location.objects.filter(company=buyer.company).annotate(num_users=Count('users'), num_depts=Count('departments'))
    location_form = LocationForm(request.POST or None)
    if request.method == "POST":
        if location_form.is_valid():
            save_location(location_form, buyer)
            messages.success(request, 'Location added successfully')
            return redirect('locations')
        else:
            messages.error(request, 'Error. Location not updated.')    
    data = {
        'locations': locations,
        'location_form': location_form,
    }
    return render(request, "settings/locations.html", data)

@login_required
def view_location(request, location_id, location_name):
    buyer = request.user.buyer_profile
    currency = buyer.company.currency

    location = get_object_or_404(Location, pk=location_id)
    location_form = LocationForm(request.POST or None, instance=location)
    
    buyers = BuyerProfile.objects.filter(location=location)
    user_form = AddUserForm(request.POST or None)
    buyer_profile_form = BuyerProfileForm(request.POST or None)
    buyer_profile_form.fields['department'].queryset = Department.objects.filter(location=location)
    
    departments = Department.objects.filter(location=location)
    department_form = DepartmentForm(request.POST or None)
    
    if request.method == "POST":
        # pdb.set_trace()
        if 'add_Location' in request.POST:
            print 'addLocation'
            if location_form.is_valid():
                save_location(location_form, buyer)
                messages.success(request, 'Location updated successfully')
            else:
                messages.error(request, 'Error. Location not updated. Please try again.')
        elif 'add_User' in request.POST:
            print 'addUser'
            if user_form.is_valid() and buyer_profile_form.is_valid():                
                user = save_user(user_form, buyer_profile_form, buyer.company, location)                
                send_verific_email(user, user.id*settings.SCALAR)
                messages.success(request, 'User successfully invited')                
            else:
                messages.error(request, 'Error. User not added. Please try again.')
        elif 'add_Department' in request.POST:
            print 'addDept'
            if department_form.is_valid():
                save_department(department_form, buyer, location)                
                messages.success(request, 'Department added successfully')                
            else:
                messages.error(request, 'Error. Department not added. Please try again.')
        return redirect('view_location', location.id, location.name)
    data = {
        'location': location,
        'location_form': location_form,
        
        'buyers': buyers,
        'user_form': user_form,
        'buyer_profile_form': buyer_profile_form,
        'user_table_headers': ['Username', 'Email', 'Department', 'Role', 'Status'],

        'departments': departments,
        'department_form': department_form,
        'dept_table_headers': ['Name', 'Annual budget ('+currency+')'],        
    }
    return render(request, "settings/view_location.html", data)

@login_required
def account_codes(request):
    buyer = request.user.buyer_profile
    account_codes = AccountCode.objects.filter(company=request.user.buyer_profile.company)    
    account_code_form = AccountCodeForm(request.POST or None)    
    account_code_form.fields['departments'].queryset = Department.objects.filter(location__in=buyer.company.get_all_locations())
    if request.method == "POST":
        if account_code_form.is_valid():
            code = account_code_form.save(commit=False)
            code.company = buyer.company
            code.save()
            account_code_form.save_m2m() #Save dept m2m field
            messages.success(request, 'Account Code added successfully')
            return redirect('account_codes')
        else:
            messages.error(request, 'Error. Account Code list not updated.')
    data = {
        'account_codes': account_codes,
        'account_code_form': account_code_form,
        'table_headers': ['Code', 'Name', 'Departments']
    }
    return render(request, "settings/account_codes.html", data)

@login_required
def approval_routing(request):
    buyer = request.user.buyer_profile
    approver_form = ApprovalRoutingForm(request.POST or None)
    # Only show 'Approvers/SuperUsers' in the dropdown
    approvers = BuyerProfile.objects.filter(company=buyer.company, role__in=['Approver', 'SuperUser'])
    approver_form.fields['approver'].queryset = approvers    
    if request.method == "POST":
        if approver_form.is_valid():
            approver_form.save()
            messages.success(request, 'Approver added successfully')
            return redirect('approval_routing')
        else:
            messages.error(request, 'Error. New Approval Route not set up.')
    data = {
        'approver_form': approver_form,
        'approvers': approvers,
        'table_headers': ['Approver', 'Location (Dept.)', 'Threshold ('+buyer.company.currency+')']
    }
    return render(request, "settings/approval_routing.html", data)

@login_required
def products(request):
    buyer = request.user.buyer_profile
    products = CatalogItem.objects.filter(buyer_co=request.user.buyer_profile.company)
    product_form = CatalogItemForm(request.POST or None)
    product_form.fields['category'].queryset = Category.objects.filter(buyer_co=buyer.company)
    product_form.fields['vendor_co'].queryset = VendorCo.objects.filter(buyer_co=buyer.company)    
    if request.method == "POST":
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.currency = product.vendor_co.currency
            product.buyer_co = buyer.company
            product.save()
            messages.success(request, "Product added successfully")
            return redirect('products')
        else:
            messages.error(request, 'Error. Catalog list not updated.')
    currency = buyer.company.currency.upper()
    data = {
        'products': products,
        'product_form': product_form,
        'table_headers': ['Name', 'SKU', 'Description', 'Price ('+currency+')', 'Unit', 'Threshold', 'Category', 'Vendor'],
    }
    return render(request, "settings/catalog.html", data)

@login_required
def upload_product_csv(request):
    csv_form = UploadCSVForm(request.POST or None, request.FILES or None)
    buyer = request.user.buyer_profile
    if request.method == "POST":
        if csv_form.is_valid():       
            reader = csv.DictReader(request.FILES['file'])
            try:                
                handle_product_upload(reader, buyer.company)                
                messages.success(request, 'Products successfully uploaded.')
                return redirect('products')
            except:
                messages.error(request, 'Error. Not all products uploaded. Please ensure all fields are correctly filled in and try again.')
    data = {
        'csv_form': csv_form,
    }
    return render(request, "settings/catalog_import.html", data)

@login_required
def vendors(request):
    vendors = VendorCo.objects.filter(buyer_co=request.user.buyer_profile.company)
    vendor_form = VendorCoForm(request.POST or None)
    location_form = LocationForm(request.POST or None)
    if request.method == "POST":
        if vendor_form.is_valid() and location_form.is_valid():
            vendor = vendor_form.save()
            vendor.currency = request.user.buyer_profile.company.currency
            vendor.buyer_co = request.user.buyer_profile.company
            vendor.save()
            location = location_form.save(commit=False)
            location.company = vendor
            location.save()
            messages.success(request, "Vendor added successfully")
            return redirect('vendors')
        else:
            messages.error(request, 'Error. Vendor list not updated.')
    data = {
        'vendors': vendors,
        'vendor_form': vendor_form,
        'location_form': location_form,
        'table_headers': ['Name', 'Contact', 'Location']
    }
    return render(request, "settings/vendors.html", data)    

@login_required
def view_vendor(request, vendor_id, vendor_name):
    vendor = get_object_or_404(VendorCo, pk=vendor_id)
    location = Location.objects.filter(company=vendor)[0]
    vendor_form = VendorCoForm(request.POST or None, instance=vendor)
    location_form = LocationForm(request.POST or None, instance=location)
    doc_ids = [doc.id for doc in vendor.invoice.all()]
    documents = File.objects.filter(document__in=doc_ids)
    if request.method == 'POST':
        if vendor_form.is_valid() and location_form.is_valid():
            vendor = vendor_form.save()
            location = location_form.save()
            messages.success(request, "Vendor updated successfully")
        else:
            messages.error(request, 'Error. Vendor not updated.')
    data = {
        'vendor': vendor,
        'vendor_form': vendor_form,
        'location_form': location_form,
        'documents': documents,
    }
    return render(request, "settings/view_vendor.html", data)    

@login_required
def upload_vendor_csv(request):
    csv_form = UploadCSVForm(request.POST or None, request.FILES or None)
    buyer = request.user.buyer_profile
    currency = buyer.company.currency.upper()
    if request.method == "POST":
        if csv_form.is_valid():
            reader = csv.DictReader(request.FILES['file'])
            try:                
                handle_vendor_upload(reader, buyer.company, currency)
                messages.success(request, 'Vendor list successfully uploaded.')
                return redirect('vendors')
            except:
                messages.error(request, 'Error. Not all vendors uploaded. Please ensure all fields are correctly filled in and try again.')
    data = {
        'csv_form': csv_form,
    }
    return render(request, "settings/vendor_import.html", data)

@login_required
def categories(request):
    categories = Category.objects.filter(buyer_co=request.user.buyer_profile.company)
    category_form = CategoryForm(request.POST or None)
    if request.method == "POST":
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.buyer_co = request.user.buyer_profile.company
            category.save()
            messages.success(request, "Category added successfully")
            return redirect('categories')   
        else:
            messages.error(request, 'Error. Category list not updated.')
    data = {
        'categories': categories,
        'category_form': category_form,
        'table_headers': ['Code', 'Name',]
    }
    return render(request, "settings/categories.html", data)   

@login_required
def user_profile(request):
    user_form = ChangeUserForm(request.POST or None, instance=request.user)   #TODO: Ensure PW doesn't show in the form
    # buyer_profile_form = BuyerProfileForm(request.POST or None, instance=request.user.buyer_profile)
    if request.method == "POST":
        if user_form.is_valid():
            user_form.save()
            # buyer_profile_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('user_profile')
        else:
            messages.error(request, 'Error. Profile not updated')
    data = {
        'user_form': user_form,
        # 'buyer_profile_form': buyer_profile_form
    }
    return render(request, "settings/user_profile.html", data)    

# DONE
@login_required
def company_profile(request):
    buyer = request.user.buyer_profile
    company_form = BuyerCoForm(request.POST or None, instance=buyer.company)
    if request.method == "POST":
        if 'company' in request.POST:
            if company_form.is_valid():
                company_form.save()
                messages.success(request, "Company profile updated successfully")
                return redirect('company_profile')     
        else:
            messages.error(request, 'Error. Settings not updated')        
    data = {
        'company_form': company_form,
        'currency': buyer.company.currency,
    }
    return render(request, "settings/company_profile.html", data)  