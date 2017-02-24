from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login as auth_login
from django.conf import settings as conf_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.forms import UserChangeForm
from django.core.serializers import serialize
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Sum, Max, Avg, F, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import inlineformset_factory,BaseModelFormSet, formset_factory, modelformset_factory
from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.template.response import TemplateResponse
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.urls import reverse
from django.utils import timezone
from django.utils.http import is_safe_url
from django.utils.text import slugify
from datetime import datetime, timedelta
from rest_framework.renderers import JSONRenderer
from eProc.models import *
from eProc.serializers import *
from eProc.forms import *
from eProc.utils import *
from collections import defaultdict
import csv
from itertools import chain
import pdb
from random import randint
import unicodedata


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
            buyer_profile = BuyerProfile.objects.create(role='SuperUser', user=user_instance, department=department, location=location, company=company)
            messages.info(request, "Thank you for registering. You are now logged in.")
            save_notification('Welcome! Super pumped to have you join the family!', 'Success', [request.user])
            user = authenticate(username=user_form.cleaned_data['username'],password=user_form.cleaned_data['password1'])
            user.is_active=False #User not active until activate account through email
            user.save()
            send_verific_email(user, user.id*conf_settings.SCALAR)
            return redirect('thankyou')
        else:
            messages.info(request, 'Error. Registration unsuccessful') #TODO: Figure out how to show errors
    data = {
        'user_form': user_form,
        'buyer_company_form': buyer_company_form
    }
    return render(request, "registration/register.html", data)

def activate(request):
    user_id = int(request.GET.get('id'))/conf_settings.SCALAR
    try:
        user = User.objects.get(id=user_id)
        user.is_active=True
        user.save()
        save_notification('Welcome! Super pumped to have you join the family!', 'Success', [user])
        save_notification('User '+user.username+' is now active', 'Success', [request.user])
    except:
        save_notification('User '+user.username+' was not activated', 'Error', [request.user])
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
            ['locations','1. Add locations & departments', Department.objects.filter(location__company=buyer.company).exists()],
            ['vendors','2. Add vendors', VendorCo.objects.filter(buyer_cos=buyer.company).exists()],
            ['categories','3. Create product categories', Category.objects.filter(buyer_co=buyer.company).exists()],
            ['products','4. Add items to catalog', CatalogItem.objects.filter(buyer_cos=buyer.company).exists()],
            ['account_codes','4. Create account codes', AccountCode.objects.filter(company=buyer.company).exists()],
            ['approval_routing','5. Set up approval routing', BuyerProfile.objects.filter(company=buyer.company, approval_threshold__gt=100).exists()],
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
            ['new_invoice_items','1. Track invoices', invoice_exists],
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
    
    # Order Items with current_status = 'Delivered PARTIAL/COMLPETE', in the past 7 days
    items_received = OrderItem.objects.filter(current_status__in=conf_settings.DELIVERED_STATUSES)
    items_received_this_week = items_received.annotate(latest_update=Max('status_updates__date')).filter(latest_update__gte=datetime.now()-timedelta(days=7))

    data = {
        # DASHBOARD FOR SUPERUSER
        'pending_requisitions': Requisition.latest_status_objects.pending.filter(pk__in=requisitions),
        'pending_pos': PurchaseOrder.latest_status_objects.pending.filter(pk__in=pos),
        'items_received': items_received,

        # DASHBOARD FOR AVERAGE USER
    }
    return render(request, "main/dashboard.html", data)


####################################
###        REQUISITIONS          ### 
####################################

@login_required
def new_requisition(request): 
    buyer = request.user.buyer_profile
    requisition_form = RequisitionForm(request.POST or None,
                                       initial= {'number': "RO"+str(Requisition.objects.filter(buyer_co=buyer.company).count()+1)})        
    OrderItemFormset = inlineformset_factory(parent_model=Requisition, model=OrderItem, form=NewReqItemForm, extra=1)
    orderitem_formset = OrderItemFormset(request.POST or None)
    initialize_req_form(buyer, requisition_form, orderitem_formset)
    
    if request.method == "POST":
        users = get_users_for_notifications(['SuperUser', 'Approver'], requisition.preparer)
        if requisition_form.is_valid() and orderitem_formset.is_valid():            
            # Save order_items and statuses (Req & Order Item status) --> see utils.py
            requisition = save_new_document(buyer, requisition_form)
            save_new_requisition_items(buyer, requisition, orderitem_formset)
            if buyer.role == 'SuperUser':
                save_status(document=requisition, doc_status='Approved', item_status='Approved', author=buyer)                
                save_notification('Requisition '+requisition.number+' has been approved', 'Success', users, target='requisitions')
            else:
                save_status(document=requisition, doc_status='Pending', item_status='Requested', author=buyer)
                save_notification('Requisition '+requisition.number+' is pending your approval', 'Success', requisition.next_approver.user, target='requisitions')
            messages.success(request, 'Requisition submitted successfully')
            return redirect('requisitions')
        else:
            messages.info(request, 'Error. Requisition not submitted')
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

    ApproveReqItemFormset = inlineformset_factory(Requisition, OrderItem, ApproveReqItemForm, extra=0)
    approve_req_formset = ApproveReqItemFormset(request.POST or None, instance=requisition)

    # Manage approving/denying requisitions (see utils.py)
    if request.method == 'POST':
        users = get_users_for_notifications(['SuperUser', 'Approver'], requisition.preparer)
        if approve_req_formset.is_valid():
            if 'approve' in request.POST:
                save_approved_requisition_items(buyer, requisition, approve_req_formset)
                save_notification('Requisition '+requisition.number+' has been approved', 'Success', users, target='requisitions')
                messages.success(request, 'Requisition approved')
            elif 'deny' in request.POST:
                save_denied_cancelled_requisition_items(buyer, requisition, approve_req_formset, 'Denied')
                save_notification('Requisition '+requisition.number+' has been denied', 'Warning', users, target='requisitions')
                messages.success(request, 'Requisition denied')
            elif 'cancel' in request.POST:
                save_denied_cancelled_requisition_items(buyer, requisition, approve_req_formset, 'Cancelled')
                messages.success(request, 'Requisition Cancelled')          
            else:
                messages.info(request, 'Error. Requisition not updated')
            return redirect('requisitions')
    data = {
        'requisition': requisition,
        'approve_req_formset': approve_req_formset,
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
    
    # Get list of Order Items with current_status = 'Approved' from the company
    # ...excluding those where the PO has already been allocated (#Assuming 1 item has 1PO for now)
    approved_order_items = OrderItem.objects.filter(current_status='Approved', requisition__buyer_co=buyer.company).exclude(purchase_order__isnull=False)
        
    if request.method == 'POST':
        # Get items selected and convert to comma-separated string
        items = request.POST.getlist('order_items')
        item_ids = ','.join(items)
        
        # Redirect to new_po_confirm with query parameters = ids of items
        redirect_url = reverse('new_po_confirm')
        query_params = '?item_ids=' + str(item_ids)
        return HttpResponseRedirect (redirect_url + query_params)

    data = {
        'approved_order_items': approved_order_items,
        'table_headers': ['', 'Order No.', 'Item', 'Qty Approved', 'Vendor', 'Date Required', 'Cost'], 
    }
    return render(request, "pos/new_po_items.html", data)

@login_required
def new_po_confirm(request):    
    buyer = request.user.buyer_profile
    currency = buyer.company.currency

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
            users = get_users_for_notifications(['SuperUser', 'Purchaser'], purchase_order.preparer)            
            save_status(document=purchase_order, doc_status='Open', item_status='Ordered', author=buyer)
            save_new_po_items(buyer, purchase_order, po_items_formset)            
            save_notification('PO '+purchase_order.number+' has been created', 'Success', users, target='purchaseorders')
            messages.success(request, 'PO created successfully')
            return redirect('purchaseorders')
        else:
            messages.info(request, 'Error. Purchase order not created')
    
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
        'open_pos': PurchaseOrder.latest_status_objects.opened.filter(pk__in=pos),
        'closed_pos': PurchaseOrder.latest_status_objects.closed.filter(pk__in=pos),
        'paid_pos': pos.filter(is_paid=True),
        'cancelled_pos': PurchaseOrder.latest_status_objects.cancelled.filter(pk__in=pos),
    }
    return render(request, "pos/purchaseorders.html", data)

@login_required
def print_po(request, po_id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
    data = {
        'purchase_order': purchase_order,        
    }
    return render(request, "pos/print_po.html", data)

@login_required
def view_po(request, po_id):
    buyer = request.user.buyer_profile
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
    if request.method == 'POST':
        users = get_users_for_notifications(['SuperUser', 'Purchaser'], purchase_order.preparer)
        if 'close' in request.POST:            
            DocumentStatus.objects.create(value='Closed', author=buyer, document=purchase_order)
            # No Order Item status updates needed because 'Close' only shows if purchase_order.is_ready_to_close
            # which is all items of purchase_order have current_status 'Delivered Complete'
            messages.success(request, 'Purchase Order closed')  
            save_notification('PO '+purchase_order.number+' has been closed', 'Success', users, target='purchaseorders')          
            return redirect('purchaseorders')
        elif 'cancel' in request.POST:
            # PO is Cancelled, Items go back into Approved list, PO delinked
            save_cancelled_po_items(buyer, purchase_order)
            messages.success(request, 'PO Cancelled')            
            return redirect('purchaseorders')
        elif 'paid' in request.POST:
            purchase_order.is_paid = True
            purchase_order.save()
            messages.success(request, 'PO marked as Paid') 
            save_notification('PO '+purchase_order.number+' has been paid', 'Success', users, target='purchaseorders')
            return redirect('purchaseorders')
        else:
            messages.info(request, 'Error. PO not updated')        
    data = {
        'purchase_order': purchase_order,
    }
    return render(request, "pos/view_po.html", data)

@login_required
def receive_pos(request):
    buyer = request.user.buyer_profile
    pos = get_documents_by_auth(buyer, PurchaseOrder)
    data = {
        'open_pos': PurchaseOrder.latest_status_objects.opened.filter(pk__in=pos),
    }
    return render(request, "pos/receive_pos.html", data)

@login_required
def receive_po(request, po_id):
    buyer = request.user.buyer_profile
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
    ReceivePOItemFormSet = inlineformset_factory(PurchaseOrder, OrderItem, ReceivePOItemForm, extra=0)
    receive_po_formset = ReceivePOItemFormSet(request.POST or None, instance=purchase_order)
    receipt_file_form = FileForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':        
        if receipt_file_form.is_valid() and receive_po_formset.is_valid():
            users = get_users_for_notifications(['SuperUser', 'Purchaser'], purchase_order.preparer)
            
            # If a file was uploaded, save it to PO
            if len(request.FILES) != 0:  
                save_file_to_doc(receipt_file_form, 'Receipt slip', request.FILES['file'], purchase_order)            
            
            save_received_po_items(buyer, receive_po_formset)
            messages.success(request, 'PO updated')
            return redirect('receive_po', purchase_order.pk)
        else:
            messages.info(request, 'Error updating items')            
    data = {
        'purchase_order': purchase_order,
        'receipt_file_form': receipt_file_form,
        'receive_po_formset': receive_po_formset,
    }
    return render(request, "pos/receive_po.html", data)

@login_required
def po_orderitems(request, po_id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
    buyer_co = request.user.buyer_profile.company
    try:
        # Get relevant PO orderItems and serialize the data into json for ajax request
        order_items = OrderItem.objects.filter(purchase_order=purchase_order)
        data = POItemSerializer(order_items, many=True).data
    except TypeError:
        data = []
    return HttpResponse(JSONRenderer().render(data), content_type='application/json')


####################################
###     INVOICES & A/PAYABLE     ### 
####################################

@login_required
def new_invoice_items(request):
    buyer = request.user.buyer_profile
    
    # Set up Vendor Selection form    
    vendorForm = VendorForm(request.POST or None)
    vendorForm.fields['name'].queryset = VendorCo.objects.filter(buyer_cos=buyer.company)

    if request.method == 'POST':
        if vendorForm.is_valid():
            vendor = vendorForm.cleaned_data['name']

            # Get items selected and convert to comma-separated string        
            items = request.POST.getlist('order_items')
            item_ids = ','.join(items)
            
            # Redirect to new_invoice_confirm with query parameters = ids of items
            redirect_url = reverse('new_invoice_confirm')
            query_params = '?item_ids=' + str(item_ids) + '&vendor=' + str(vendor.pk)
            return HttpResponseRedirect (redirect_url + query_params)

    data = {
        'vendorForm': vendorForm,
        'currency': buyer.company.currency,
        'table_headers': ['', 'PO', 'Item', 'Qty Delivered', 'Cost'],
    }
    return render(request, "invoices/new_invoice_items.html", data)

@login_required
def new_invoice_confirm(request):
    buyer = request.user.buyer_profile
    currency = buyer.company.currency

    # Get the items selected in new_invoice_items from the query parameter
    item_ids = request.GET.get('item_ids')
    item_id_array = item_ids.split(",")
    items = OrderItem.objects.filter(id__in=item_id_array)

    # Get the vendor_co selected in new_invoice_items from the query parameter
    vendor_id = request.GET.get('vendor')
    vendor = VendorCo.objects.get(id=vendor_id)

    # Prefix so the name field (common to both forms) isn't confused
    invoice_form = InvoiceForm(request.POST or None, prefix='invoice')
    initialize_invoice_form(buyer, invoice_form)
    invoice_file_form = FileForm(request.POST or None, request.FILES or None)
        
    if request.method == 'POST':
        # pdb.set_trace()
        if invoice_form.is_valid() and invoice_file_form.is_valid():
            # Basic form validations 
            if len(request.FILES) == 0:
                messages.info(request, 'Error. Invoice file is required.')

            else:
                invoice = save_new_document(buyer, invoice_form)  #Note: Invoice hasn't been saved yet
                save_new_invoice_items(buyer, invoice, items, vendor)
                users = get_users_for_notifications(['SuperUser', 'Purchaser'], invoice.preparer)                
                save_file_to_doc(invoice_file_form, 'Vendor Invoice', request.FILES['file'], invoice)                
                save_notification('PO '+invoice.number+' has been created', 'Success', users, target='invoices')
                messages.success(request, 'Invoice created successfully')
                return redirect('invoices')
        else:
            messages.info(request, 'Error. Ensure all fields and files are filled in.')

    data = {
        'items': items,
        'vendor': vendor,
        'invoice_form': invoice_form,
        'invoice_file_form': invoice_file_form,     
        'currency': currency,    
    }
    return render(request, "invoices/new_invoice_confirm.html", data)

# AJAX request used to update new_invoice_items list
@login_required
def unbilled_items_by_vendor(request, vendor_id):
    buyer = request.user.buyer_profile        
    vendor_co = get_object_or_404(VendorCo, pk=vendor_id)
    try:
        # Order Items with current_status = Ordered/Delivered, isn't linked to an invoice, and whose PO is with the specific vendor_id
        unbilled_items = OrderItem.objects.filter(current_status__in=conf_settings.UNBILLED_STATUSES, invoice__isnull=True, requisition__buyer_co=buyer.company, purchase_order__vendor_co=vendor_co)
        data = UnbilledItemSerializer(unbilled_items, many=True).data
    except TypeError:
        data = []
    # Serialize the data into json for ajax request
    return HttpResponse(JSONRenderer().render(data), content_type='application/json')

@login_required
def invoices(request):
    buyer = request.user.buyer_profile    
    
    # Returns Invoices where the user is either the preparer OR next_approver, unless user is SuperUser (see utils.py)
    invoices = get_documents_by_auth(buyer, Invoice)
    
    data = {
        'all_invoices': Invoice.latest_status_objects.filter(pk__in=invoices),
        'pending_invoices': Invoice.latest_status_objects.pending.filter(pk__in=invoices),
        'approved_invoices': Invoice.latest_status_objects.approved.filter(pk__in=invoices),
        'denied_invoices': Invoice.latest_status_objects.denied.filter(pk__in=invoices)|Invoice.latest_status_objects.cancelled.filter(pk__in=invoices),
        'paid_invoices': invoices.filter(is_paid=True),
        'table_headers': ['Invoice', 'Grand Total', 'Invoice Created', 'Date Due', 'Vendor', 'PO', 'Files', 'Comments']
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
        users = get_users_for_notifications(['SuperUser', 'Purchaser'], invoice.preparer)
        # Only Invoice statuses updated - no changes to OrderItem.current_status or OrderItemStatuses
        if 'approve' in request.POST:
            save_doc_status(document=invoice, doc_status='Approved',author=buyer)
            save_notification('Invoice '+invoice.number+' has been approved', 'Success', users, target='invoices')
            messages.success(request, 'Invoice Approved')
        elif 'deny' in request.POST:
            save_doc_status(document=invoice, doc_status='Denied', author=buyer)
            save_notification('Invoice '+invoice.number+' has been denied', 'Warning', users, target='invoices')
            messages.success(request, 'Invoice Denied')
        elif 'cancel' in request.POST:
            save_doc_status(document=invoice, doc_status='Cancelled', author=buyer)
            messages.success(request, 'Invoice Cancelled')
        elif 'paid' in request.POST:
            invoice.is_paid = True
            invoice.save()
            save_notification('Invoice '+invoice.number+' has been marked as paid', 'Success', users, target='invoices')
            messages.success(request, 'Invoice marked as Paid')
        else:
            messages.info(request, 'Error. Invoice not updated')
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

@login_required
def unbilled_items(request):
    buyer = request.user.buyer_profile

    # Order Items with current_status = Ordered/Delivered, isn't linked to an invoice
    unbilled_items = OrderItem.objects.filter(current_status__in=conf_settings.UNBILLED_STATUSES, invoice__isnull=True, requisition__buyer_co=buyer.company)

    # TODOOOO WHEN ORDER_ITEMS ARE REFINED
    # Unbilled items --> allocate to specific account codes (http://kb.procurify.com/?st_kb=accounts-payable-unbilled-items)
    # Unbilled Items Formset with editable Location/Department/AccountCode/Cost Allocation
    # UnbilledFormset = formset_factory(UnbilledItemAllocationForm, extra=1)
    # unbilled_formset = UnbilledFormset(request.POST or None)

    # if request.method == 'POST':
    #     item_id = int(request.POST.get('edit')[5:])
    #     item = get_object_or_404(OrderItem, pk=item_id)
    #     if unbilled_formset.is_valid():
    #         for form in unbilled_formset.forms:
    #             department = form.cleaned_data['department']
    #             account_code = form.cleaned_data['account_code']
    #             cost = form.cleaned_data['cost']
    #         pass
    #         messages.success(request, 'Item updated successfully')            
    #     else:
    #         messages.info(request, 'Error. Item not updated')
    #     return redirect('unbilled_items')

    data = {
        'unbilled_items':unbilled_items,
        # 'unbilled_formset': unbilled_formset,
        'table_headers': ['PO No.', 'Product', 'Delivered Date', 'Dept.', 'Qty Unbilled', 'Unit Price', 'Vendor']
    }
    return render(request, "acpayable/unbilled_items.html", data)

@login_required
def receiving_summary(request):
    buyer = request.user.buyer_profile
    
    items_received_all = OrderItem.latest_status_objects.delivered.filter(requisition__buyer_co=buyer.company)
    items_received_this_week = items_received_all.annotate(latest_update=Max('status_updates__date')).filter(latest_update__gte=datetime.now()-timedelta(days=7))
    items_received_this_month = items_received_all.annotate(latest_update=Max('status_updates__date')).filter(latest_update__gte=datetime.now()-timedelta(days=30))

    data = {
        'items_received_all': items_received_all,
        'items_received_this_week': items_received_this_week,
        'items_received_this_month': items_received_this_month,
        'table_headers': ['PO', 'Item', 'Vendor', 'Product', 'Delivery Dates', 'Recd. - Qty', 'Recd. - Amount', 'Ordered - Qty', 'Ordered - Amount', 'Recd. %']
    }
    return render(request, "acpayable/receiving_summary.html", data)

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

    data = {
        'location': location,
        'inventory_list': location.get_inventory_items(),
        'delivered_list': location.get_delivered_items(),
        'drawndown_list': location.get_drawndown_items(),
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
    DrawdownItemFormSet = inlineformset_factory(parent_model=Drawdown, model=DrawdownItem, form=DrawdownItemForm, extra=1)
    drawdownitem_formset = DrawdownItemFormSet(request.POST or None)
    initialize_drawdown_form(buyer, drawdown_form, drawdownitem_formset)    
    
    if request.method == "POST":        
        if drawdown_form.is_valid() and drawdownitem_formset.is_valid():            
            drawdown = save_new_document(buyer, drawdown_form)
            users = get_users_for_notifications(['SuperUser', 'Inventory Manager'], drawdown.preparer)
            save_new_drawdown_items(buyer, drawdown, drawdownitem_formset)
            if buyer.role == 'SuperUser':
                save_status(document=drawdown, doc_status='Approved', item_status='Approved', author=buyer)
                save_notification('Drawdown '+drawdown.number+' has been approved', 'Success', users, target='drawdowns')
            else:
                save_status(document=drawdown, doc_status='Pending', item_status='Pending', author=buyer)      
                save_notification('New Drawdown '+drawdown.number+' is pending', 'Success', users, target='drawdowns')
            messages.success(request, 'Drawdown submitted successfully')
            return redirect('drawdowns')
        else:
            messages.info(request, 'Error. Drawdown not submitted')
    data = {
        'drawdown_form': drawdown_form,
        'drawdownitem_formset': drawdownitem_formset,
        'table_headers': ['Product', 'Quantity', 'Comments'],
    }
    return render(request, "drawdowns/new_drawdown.html", data)


@login_required
def view_drawdown(request, drawdown_id):
    buyer = request.user.buyer_profile
    drawdown = get_object_or_404(Drawdown, pk=drawdown_id)     

    ApproveDDItemFormset = inlineformset_factory(Drawdown, DrawdownItem, ApproveDDItemForm, extra=0)
    approve_dd_formset = ApproveDDItemFormset(request.POST or None, instance=drawdown)

    # Manage approving/denying drawdowns (see utils.py)
    if request.method == 'POST':
        users = get_users_for_notifications(['SuperUser', 'Inventory Manager'], drawdown.preparer)
        if approve_dd_formset.is_valid():
            if 'approve' in request.POST:
                save_approved_dd_items(buyer, drawdown, approve_dd_formset)
                save_notification('Drawdown '+drawdown.number+' has been approved', 'Success', users, target='drawdowns')
                messages.success(request, 'Drawdown approved')
            elif 'deny' in request.POST:
                save_denied_cancelled_dd_items(buyer, drawdown, approve_dd_formset, 'Denied')
                save_notification('Drawdown '+drawdown.number+' has been denied', 'Warning', users, target='drawdowns')
                messages.success(request, 'Drawdown denied')
            elif 'cancel' in request.POST:
                save_denied_cancelled_dd_items(buyer, drawdown, approve_dd_formset, 'Denied')
                messages.success(request, 'Drawdown Cancelled')          
            else:
                messages.info(request, 'Error. Drawdown not updated')
            return redirect('drawdowns')
    data = {
        'drawdown': drawdown,
        'approve_dd_formset': approve_dd_formset,
        'table_headers': ['Product', 'Quantity', 'Account Code', 'Comments'],
    }
    return render(request, "drawdowns/view_drawdown.html", data)


@login_required
def print_drawdown(request, drawdown_id):
    drawdown = get_object_or_404(Drawdown, pk=drawdown_id)
    data = {
        'drawdown': drawdown,        
    }
    return render(request, "drawdowns/print_drawdown.html", data)

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
        'closed_drawdowns': Drawdown.latest_status_objects.closed.filter(pk__in=drawdowns),
        'table_headers': ['Drawdown No.', 'Requested by', 'Requested Date', 'Due Date', 'Comments']
    }
    return render(request, "drawdowns/drawdowns.html", data)

@login_required
def call_drawdowns(request):
    buyer = request.user.buyer_profile
    drawdowns = get_documents_by_auth(buyer, Drawdown)
    data = {
        'approved_drawdowns': Drawdown.latest_status_objects.approved.filter(pk__in=drawdowns),
        'table_headers': ['Drawdown No.', 'Requested by', 'Requested Date', 'Due Date', 'Comments']
    }
    return render(request, "drawdowns/call_drawdowns.html", data)

@login_required
def call_drawdown(request, drawdown_id):
    buyer = request.user.buyer_profile
    drawdown = get_object_or_404(Drawdown, pk=drawdown_id)
    CallDDItemFormSet = inlineformset_factory(Drawdown, DrawdownItem, CallDrawdownItemForm, extra=0)
    call_dd_formset = CallDDItemFormSet(request.POST or None, instance=drawdown)

    if request.method == 'POST':
        if call_dd_formset.is_valid():
            users = get_users_for_notifications(['SuperUser', 'Inventory Manager'], drawdown.preparer)
            save_called_dd_items(buyer, call_dd_formset)
            save_notification('Drawdown '+drawdown.number+' drawndown', 'Success', users, target='drawdowns')

            # If form.is_ready_to_close (qty_approved = qty_drawdown for all items), then automatically close
            if drawdown.is_ready_to_close():
                save_doc_status(drawdown, 'Closed', buyer)                        
                messages.success(request, 'Drawdown updated and closed')                        
                save_notification('Drawdown '+drawdown.number+' marked as closed', 'Success', users, target='drawdowns')
                return redirect('drawdowns')
            else:
                messages.success(request, 'Drawdown updated successfully')
                return redirect('call_drawdown', drawdown.pk)
        else:
            messages.info(request, 'Error updating items')            
    data = {
        'drawdown': drawdown,
        'call_dd_formset': call_dd_formset,
    }
    return render(request, "drawdowns/call_drawdown.html", data)

####################################
###           SETTINGS           ### 
####################################

@login_required
def settings(request):
    all_bulk_products = CatalogItem.objects.filter(item_type='Bulk Discount')
    data = {
        'all_bulk_products': all_bulk_products,
    }
    return render(request, "settings/settings.html", data)

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
        #         send_verific_email(user, user.id*conf_settings.SCALAR)
        #         messages.success(request, 'User successfully invited')
        #         return redirect('users')
        #     else:
        #         messages.info(request, 'Error adding user. Please try again.')
        if 'delete' in request.POST:          
            for key in request.POST:
                if key == 'delete':
                    buyer_id = int(request.POST[key])
                    buyer_to_delete = BuyerProfile.objects.get(pk=buyer_id)
                    user_to_delete = User.objects.get(buyer_profile=buyer_to_delete)
                    if user_to_delete == request.user:
                        messages.info(request, 'Sorry, you can not delete yourself')
                    else:
                        user_to_delete.delete()
                        buyer_to_delete.delete()
                        messages.success(request, 'User ' + user_to_delete.username + ' successfully deleted')
                        return redirect('users')
        else:
            messages.info(request, 'Error. Please try again.')
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
            messages.info(request, 'Error. Location not updated.')    
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
        if 'add_Location' in request.POST:
            if location_form.is_valid():
                save_location(location_form, buyer)
                messages.success(request, 'Location updated successfully')
            else:
                messages.info(request, 'Error. Location not updated. Please try again.')
        elif 'add_User' in request.POST:
            if user_form.is_valid() and buyer_profile_form.is_valid():                
                user = save_user(user_form, buyer_profile_form, buyer.company, location)                
                send_verific_email(user, user.id*conf_settings.SCALAR)
                messages.success(request, 'User successfully invited')         
                save_notification('User '+user.username+' has been added', 'Success', list(User.objects.filter(buyer_profile__company=buyer.company)), target='locations')       
            else:
                messages.info(request, 'Error. User not added. Please try again.')
        elif 'add_Department' in request.POST:
            if department_form.is_valid():
                department = save_department(department_form, buyer, location)                
                messages.success(request, 'Department added successfully')   
                save_notification('Department '+department.name+' has been added', 'Success', list(User.objects.filter(buyer_profile__company=buyer.company)), target='locations')
            else:
                messages.info(request, 'Error. Department not added. Please try again.')
        return redirect('view_location', location.id, slugify(location.name))
    data = {
        'location': location,
        'location_form': location_form,
        
        'buyers': buyers,
        'user_form': user_form,
        'buyer_profile_form': buyer_profile_form,
        'user_table_headers': ['Username', 'Email', 'Department', 'Role', 'Status'],

        'departments': departments,
        'department_form': department_form,
        'dept_table_headers': ['Name', 'Budget', 'Spend YTD', 'Spend % of budget'],        
    }
    return render(request, "settings/view_location.html", data)

@login_required
def account_codes(request):
    buyer = request.user.buyer_profile
    account_codes = AccountCode.objects.filter(company=buyer.company)    
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
            messages.info(request, 'Error. Account Code list not updated.')
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
            save_notification('New approver has been added', 'Success', list(User.objects.filter(buyer_profile__company=buyer.company)), target='approval_routing')
            return redirect('approval_routing')
        else:
            messages.info(request, 'Error. New Approval Route not set up.')
    data = {
        'approver_form': approver_form,
        'approvers': approvers,
        'table_headers': ['Approver', 'Location (Dept.)', 'Threshold ('+buyer.company.currency+')']
    }
    return render(request, "settings/approval_routing.html", data)

@login_required
def products(request):
    buyer = request.user.buyer_profile
    products = CatalogItem.objects.filter(buyer_cos=request.user.buyer_profile.company)
    product_form = CatalogItemForm(request.POST or None)
    product_form.fields['category'].queryset = Category.objects.filter(buyer_co=buyer.company)
    product_form.fields['vendor_co'].queryset = VendorCo.objects.filter(buyer_cos=buyer.company)    
    if request.method == "POST":
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.currency = product.vendor_co.currency
            product.save()
            product.buyer_cos.add(buyer.company)
            product.save()
            messages.success(request, "Product added successfully")
            save_notification('New product ' + product.name + 'has been added to the catalog', 'Success', list(User.objects.filter(buyer_profile__company=buyer.company)), target='products')
            return redirect('products')
        else:
            messages.info(request, 'Error. Catalog list not updated.')
    currency = buyer.company.currency.upper()
    data = {
        'products': products,
        'product_form': product_form,
        'table_headers': ['', 'Product', 'SKU', 'Description', 'Price', 'Threshold', 'Category', 'Vendor'],
    }
    return render(request, "products/products.html", data)

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
                save_notification('New products have been added to the catalog', 'Success', list(User.objects.filter(buyer_profile__company=buyer.company)), target='products')
                return redirect('products')
            except:
                messages.info(request, 'Error. Not all products uploaded. Please ensure all fields are correctly filled in and try again.')
    data = {
        'csv_form': csv_form,
    }
    return render(request, "products/catalog_import.html", data)

@login_required
def products_bulk(request):
    buyer = request.user.buyer_profile
    all_bulk_products = CatalogItem.objects.filter(item_type='Bulk Discount')
    recent_bulk_products = all_bulk_products.order_by('-pk')[:5]

    if request.method == "POST":
        if 'add' in request.POST:
            product_id = int(request.POST.get('add')[4:])
            product = CatalogItem.objects.get(id=product_id)
            product.buyer_cos.add(buyer.company)
            product.save()
            messages.success(request, 'Product added to company catalog.')
            return redirect('products_bulk')
        elif 'remove' in request.POST:
            product_id = int(request.POST.get('remove')[7:])
            product = CatalogItem.objects.get(id=product_id)
            product.buyer_cos.remove(buyer.company)
            product.save()
            messages.success(request, 'Product removed from company catalog.')
            return redirect('products_bulk')
        else:
            messages.info(request, 'Error. Product not added to your company catalog.')
    data = {
        'all_bulk_products': all_bulk_products,
        'recent_bulk_products': recent_bulk_products,
        'table_headers': ['Category', 'Product', 'Name','Description', 'Price', 'Company Catalog'],

    }
    return render(request, "products/products_bulk.html", data)

@login_required
def vendors(request):
    buyer = request.user.buyer_profile
    vendors = VendorCo.objects.filter(buyer_cos=buyer.company)
    # Prefix so the name field (common to both forms) isn't confused
    vendor_form = VendorCoForm(request.POST or None, prefix="vendor")
    location_form = LocationForm(request.POST or None, prefix="location")
    if request.method == "POST":
        if vendor_form.is_valid() and location_form.is_valid():
            save_vendor(vendor_form, buyer)
            save_location(location_form, buyer)
            messages.success(request, "Vendor added successfully")
            save_notification('New vendor ' + vendor.name + 'added', 'Success', list(User.objects.filter(buyer_profile__company=buyer.company)), target='products')
            return redirect('vendors')
        else:
            messages.info(request, 'Error. Vendor list not updated.')
    data = {
        'vendors': vendors,
        'vendor_form': vendor_form,
        'location_form': location_form,
        'table_headers': ['Name', 'Contact', 'Location', 'Avg. Rating']
    }
    return render(request, "vendors/vendors.html", data)    

@login_required
def view_vendor(request, vendor_id, vendor_name):
    vendor_co = get_object_or_404(VendorCo, pk=vendor_id)
    location = Location.objects.filter(company=vendor_co)[0]
    # Prefix so the name field (common to both forms) isn't confused
    vendor_form = VendorCoForm(request.POST or None, prefix="vendor", instance=vendor_co)
    location_form = LocationForm(request.POST or None, prefix="location", instance=location)
    doc_ids = [doc.id for doc in vendor_co.invoice.all()]
    files = File.objects.filter(document__in=doc_ids)
    if request.method == 'POST':        
        if vendor_form.is_valid() and location_form.is_valid():
            vendor_co = vendor_form.save()
            location = location_form.save()
            messages.success(request, "Vendor updated successfully")            
        else:
            messages.info(request, 'Error. Vendor not updated.')
    data = {
        'vendor_co': vendor_co,
        'vendor_form': vendor_form,
        'location_form': location_form,
        'files': files,
        'table_headers': ['File', 'Invoice Record']

    }
    return render(request, "vendors/view_vendor.html", data)    

@login_required
def upload_vendor_csv(request):
    buyer = request.user.buyer_profile
    csv_form = UploadCSVForm(request.POST or None, request.FILES or None)    
    currency = buyer.company.currency.upper()
    if request.method == "POST":
        if csv_form.is_valid():
            reader = csv.DictReader(request.FILES['file'])
            try:                
                handle_vendor_upload(reader, buyer.company, currency)
                messages.success(request, 'Vendor list successfully uploaded.')
                save_notification('New vendors have been added', 'Success', list(User.objects.filter(buyer_profile__company=buyer.company)), target='products')
                return redirect('vendors')
            except:
                messages.info(request, 'Error. Not all vendors uploaded. Please ensure all fields are correctly filled in and try again.')
    data = {
        'csv_form': csv_form,
    }
    return render(request, "vendors/vendor_import.html", data)

@login_required
def rate_vendor(request, vendor_id, vendor_name):
    buyer = request.user.buyer_profile
    vendor_co = get_object_or_404(VendorCo, pk=vendor_id)    
    
    VendorRatingFormSet = inlineformset_factory(VendorCo, Rating, VendorRatingForm, extra=0, min_num=5)
    # Convert tuple of categories to a list to set in initial data
    CATEGORIES = [(category[0]) for category in conf_settings.CATEGORIES]
    vendor_rating_formset = VendorRatingFormSet(request.POST or None, prefix='vendor', instance=vendor_co, 
        initial=[{'category': category} for category in CATEGORIES])

    if request.method == 'POST':                
        if vendor_rating_formset.is_valid():            
            for form in vendor_rating_formset:
                vendor_rating = form.save(commit=False)
                vendor_rating.rater = request.user
                vendor_rating.vendor_co = vendor_co
                vendor_rating.save()
            messages.success(request, 'Vendor ratings saved.')
            return redirect('view_vendor', vendor_co.pk, slugify(vendor_co.name))
        else:            
            messages.info(request, 'Sorry we were unable to save your rating')
    data = {
        'vendor_co': vendor_co,
        'vendor_rating_formset': vendor_rating_formset,
    }
    return render(request, "vendors/vendor_rating.html", data)    

@login_required
def categories(request):
    buyer = request.user.buyer_profile
    categories = Category.objects.filter(buyer_co=request.user.buyer_profile.company)
    category_form = CategoryForm(request.POST or None)
    if request.method == "POST":
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.buyer_co = buyer.company
            category.save()
            messages.success(request, "Category added successfully")
            save_notification('New category ' + category.name + 'added', 'Success', list(User.objects.filter(buyer_profile__company=buyer.company)), target='products')
            return redirect('categories')   
        else:
            messages.info(request, 'Error. Category list not updated.')
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
            messages.info(request, 'Error. Profile not updated')
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
            messages.info(request, 'Error. Settings not updated')        
    data = {
        'company_form': company_form,
        'currency': buyer.company.currency,
    }
    return render(request, "settings/company_profile.html", data)  


####################################
###    REPORTS & ANALYSIS        ### 
####################################

#TODO: ALL ARE VERY INEFFICIENT ON THE DB - TO REFINE

@login_required()
def spend_by_location_dept(request):
    buyer = request.user.buyer_profile

    items, periods, items_by_period = setup_analysis_data(buyer)

    location_spend = items.values('requisition__department__location__name').annotate(total_spend=Sum(F('qty_delivered')*F('price_ordered'), output_field=models.DecimalField()))    
    dept_spend = items.values('requisition__department__name').annotate(total_spend=Sum(F('qty_delivered')*F('price_ordered'), output_field=models.DecimalField()))

    # Declare all variables
    location_spend_labels, location_spend_data, dept_spend_labels, dept_spend_data = [], [], [], []
    location_period_spend_data, dept_period_spend_data = {}, {                
        # 'loc_name/dept_name': [spend_old, spend_mid, spend_today],
    }
    
    # Set up for the arrays that are passed into charts.js (see utils.py)
    location_spend_labels, location_spend_data, location_period_spend_data = get_spend_by('requisition__department__location__name', location_spend, location_spend_labels, location_spend_data, location_period_spend_data)
    dept_spend_labels, dept_spend_data, dept_period_spend_data = get_spend_by('requisition__department__name', dept_spend, dept_spend_labels, dept_spend_data, dept_period_spend_data)

    # Get the spend values by period by location/dept
    location_period_spend_data = get_period_spend_values('requisition__department__location__name', items_by_period, location_period_spend_data)
    dept_period_spend_data = get_period_spend_values('requisition__department__name', items_by_period, dept_period_spend_data)
    
    data = {
        'items': items,
        'periods': periods,

        'location_spend_labels': location_spend_labels,
        'location_spend_data': location_spend_data,      
        'location_period_spend_data': location_period_spend_data,  #location_period_spend_labels = periods

        'dept_spend_labels': dept_spend_labels,
        'dept_spend_data': dept_spend_data,
        'dept_period_spend_data': dept_period_spend_data,   #dept_period_spend_labels = periods
    }    
    return render(request, "analysis/spend_by_location_dept.html", data)

@login_required()
def spend_by_product_category(request):
    buyer = request.user.buyer_profile

    items, periods, items_by_period = setup_analysis_data(buyer)

    category_spend = items.values('product__category__name').annotate(total_spend=Sum(F('qty_delivered')*F('price_ordered'), output_field=models.DecimalField()))    
    product_spend = items.values('product__name').annotate(total_spend=Sum(F('qty_delivered')*F('price_ordered'), output_field=models.DecimalField()))

    # Declare all variables
    category_spend_labels, category_spend_data, product_spend_labels, product_spend_data = [], [], [], []
    category_period_spend_data, product_period_spend_data = {}, {}
    
    # Set up for the arrays that are passed into charts.js (see utils.py)
    category_spend_labels, category_spend_data, category_period_spend_data = get_spend_by('product__category__name', category_spend, category_spend_labels, category_spend_data, category_period_spend_data)
    product_spend_labels, product_spend_data, product_period_spend_data = get_spend_by('product__name', product_spend, product_spend_labels, product_spend_data, product_period_spend_data)

    # Get the spend values by period by location/dept
    category_period_spend_data = get_period_spend_values('product__category__name', items_by_period, category_period_spend_data)
    product_period_spend_data = get_period_spend_values('product__name', items_by_period, product_period_spend_data)
    
    data = {
        'items': items,
        'periods': periods,

        'category_spend_labels': category_spend_labels,
        'category_spend_data': category_spend_data,      
        'category_period_spend_data': category_period_spend_data,

        'product_spend_labels': product_spend_labels,
        'product_spend_data': product_spend_data,
        'product_period_spend_data': product_period_spend_data,
    }    
    return render(request, "analysis/spend_by_product_category.html", data)

@login_required()
def spend_by_entity(request):
    buyer = request.user.buyer_profile

    items, periods, items_by_period = setup_analysis_data(buyer)

    vendor_spend = items.values('product__vendor_co__name').annotate(total_spend=Sum(F('qty_delivered')*F('price_ordered'), output_field=models.DecimalField()))    
    approver_spend = items.values('requisition__next_approver__user__username').annotate(total_spend=Sum(F('qty_delivered')*F('price_ordered'), output_field=models.DecimalField()))
    requester_spend = items.values('requisition__preparer__user__username').annotate(total_spend=Sum(F('qty_delivered')*F('price_ordered'), output_field=models.DecimalField()))    

    # Declare all variables
    vendor_spend_labels, vendor_spend_data, approver_spend_labels, approver_spend_data, requester_spend_labels, requester_spend_data = [], [], [], [], [], []
    vendor_period_spend_data, approver_period_spend_data, requester_period_spend_data = {}, {}, {}
    
    # Set up for the arrays that are passed into charts.js (see utils.py)
    vendor_spend_labels, vendor_spend_data, vendor_period_spend_data = get_spend_by('product__vendor_co__name', vendor_spend, vendor_spend_labels, vendor_spend_data, vendor_period_spend_data)
    approver_spend_labels, approver_spend_data, approver_period_spend_data = get_spend_by('requisition__next_approver__user__username', approver_spend, approver_spend_labels, approver_spend_data, approver_period_spend_data)
    requester_spend_labels, requester_spend_data, requester_period_spend_data = get_spend_by('requisition__preparer__user__username', requester_spend, requester_spend_labels, requester_spend_data, requester_period_spend_data)

    # Get the spend values by period by location/dept
    vendor_period_spend_data = get_period_spend_values('product__vendor_co__name', items_by_period, vendor_period_spend_data)
    approver_period_spend_data = get_period_spend_values('requisition__next_approver__user__username', items_by_period, approver_period_spend_data)
    requester_period_spend_data = get_period_spend_values('requisition__preparer__user__username', items_by_period, requester_period_spend_data)
    
    data = {
        'items': items,
        'periods': periods,

        'vendor_spend_labels': vendor_spend_labels,
        'vendor_spend_data': vendor_spend_data,      
        'vendor_period_spend_data': vendor_period_spend_data,

        'approver_spend_labels': approver_spend_labels,
        'approver_spend_data': approver_spend_data,
        'approver_period_spend_data': approver_period_spend_data,

        'requester_spend_labels': requester_spend_labels,
        'requester_spend_data': requester_spend_data,
        'requester_period_spend_data': requester_period_spend_data,
    } 
  
    return render(request, "analysis/spend_by_entity.html", data)

import math 
@login_required()
def industry_benchmarks(request):
    buyer = request.user.buyer_profile

    ##### CHART 1: SUPPLIER SPEND TOP 5% #####
    benchmark_spend_percent = 90
    # Order Items with latest_status = 'Delivered PARTIAL/COMLPETE' (see managers.py) in the requester's department
    items = OrderItem.objects.filter(current_status__in=conf_settings.DELIVERED_STATUSES, requisition__buyer_co=buyer.company)
    
    items_by_vendor = items.values('product__vendor_co__name').annotate(total_spend=Sum(F('qty_delivered')*F('price_ordered'), output_field=models.DecimalField()))
    
    # Calculating # suppliers that is 5%, rounded down, and at least 1 (else error in top_supplier_spend)
    # Best practices - 90% of spend should go to 5% of suppliers
    num_suppliers =  max(1, math.floor(0.05 * VendorCo.objects.filter(buyer_cos=buyer.company).count()))
    top_supplier_spend = items_by_vendor.order_by('-total_spend')[:num_suppliers].aggregate(Sum('total_spend'))['total_spend__sum']
    total_supplier_spend = items_by_vendor.aggregate(Sum('total_spend'))['total_spend__sum']
    try:
        top_supplier_spend_percent = top_supplier_spend/total_supplier_spend*100
    except TypeError:
        top_supplier_spend_percent = 0

    # Red if underperforming; Green otherwise
    buyer_co_color ='#ff6961' if top_supplier_spend_percent < 90 else '#89E894'    

    data = {
        'items': items,
        'top_supplier_spend_percent': round(top_supplier_spend_percent,2),
        'benchmark_spend_percent': benchmark_spend_percent,
        'buyer_co_color': buyer_co_color,

        # 'top_supplier_spend_competitors': top_supplier_spend_competitors,
    }
    return render(request, "analysis/industry_benchmarks.html", data)







