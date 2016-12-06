from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login as auth_login
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.forms import UserChangeForm
from django.core.serializers import serialize
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Sum, Max, F, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import inlineformset_factory,BaseModelFormSet
from django.shortcuts import render, redirect, resolve_url
from django.template.response import TemplateResponse
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils import timezone
from django.utils.http import is_safe_url
from rest_framework.renderers import JSONRenderer
from eProc.models import *
from eProc.serializers import *
from eProc.forms import *
from eProc.utils import *
import csv
import pdb

scalar = 570

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
            department = Department.objects.create(name='Admin', company=company)
            buyer_profile = BuyerProfile.objects.create(role='SuperUser', user=user_instance, department=department, company=company)
            messages.info(request, "Thank you for registering. You are now logged in.")
            user = authenticate(username=user_form.cleaned_data['username'],password=user_form.cleaned_data['password1'])
            user.is_active=False #User not active until activate account through email
            user.save()
            send_verific_email(user, user.id*scalar)
            return redirect('thankyou')
        else:
            messages.error(request, 'Error. Registration unsuccessful') #TODO: Figure out how to show errors
    data = {
        'user_form': user_form,
        'buyer_company_form': buyer_company_form
    }
    return render(request, "registration/register.html", data)

def activate(request):
    user_id = int(request.GET.get('id'))/scalar
    user = User.objects.get(id=user_id)
    user.is_active=True
    user.save()
    return render(request,'registration/activate.html')

####################################
###         MAIN PAGES           ### 
####################################

def thankyou(request):
    return render(request, 'registration/thankyou.html')
    
@login_required()
def get_started(request):
    return render(request, "main/get_started.html")

@login_required()
def dashboard(request):
    buyer = request.user.buyer_profile
    
    requisitions = Requisition.objects.filter(buyer_co=buyer.company)
    all_requisitions, pending_requisitions, approved_requisitions, denied_requisitions = get_requisitions(requisitions)
    
    pos = PurchaseOrder.objects.filter(buyer_co=buyer.company)
    all_pos, open_pos, closed_pos, cancelled_pos, paid_pos = get_pos(pos)
    
    # pending_requisitions = all_requisitions.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Pending')    
    # pending_pos = all_pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Open')
    
    all_items = OrderItem.objects.filter(requisition__buyer_co=buyer.company)
    items_received = all_items.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Delivered')

    dept_spend = items_received.values('requisition__department__name').annotate(total_cost=Sum(F('quantity')*F('unit_price'), output_field=models.DecimalField()))
    categ_spend = items_received.values('product__category__name').annotate(total_cost=Sum(F('quantity')*F('unit_price'), output_field=models.DecimalField()))
    product_spend = items_received.values('product__name').annotate(total_cost=Sum(F('quantity')*F('unit_price'), output_field=models.DecimalField()))
    data = {
        'pending_req_count': len(pending_requisitions),
        'pending_po_count': len(open_pos),
        'items_recd_count': len(items_received),
        'dept_spend': dept_spend,
        'categ_spend': categ_spend,
        'product_spend': product_spend,        
    }
    return render(request, "main/dashboard.html", data)

####################################
###           SETTINGS           ### 
####################################

@login_required
def users(request):    
    user_form = AddUserForm(request.POST or None)
    buyer_profile_form = BuyerProfileForm(request.POST or None)
    buyer_profile_form.fields['department'].queryset = Department.objects.filter(company=request.user.buyer_profile.company)
    if request.method == "POST":
        # pdb.set_trace()
        if 'add' in request.POST:
            if user_form.is_valid() and buyer_profile_form.is_valid():
                try:
                    user = user_form.save()
                    buyer_profile = buyer_profile_form.save(commit=False)
                    buyer_profile.user = user
                    buyer_profile.company = request.user.buyer_profile.company
                    buyer_profile.save()
                    send_verific_email(user, user.id*scalar)
                    messages.success(request, 'User successfully invited')
                    return redirect('users')
                #TODO: CHECK FOR VALIDATION ERROR IN FORMS.PY
                except:
                    pass
                # except ValidationError: 
                #     messages.error(request, 'Duplicate username. Please try again.')
                #     return redirect('users')
        elif 'delete' in request.POST:          
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
    buyers = BuyerProfile.objects.filter(company=request.user.buyer_profile.company)
    data = {
        'buyers': buyers,
        'user_form': user_form,
        'buyer_profile_form': buyer_profile_form,
        'table_headers': ['Username', 'Email Address', 'Role', 'Status', ' ',]
    }
    return render(request, "settings/users.html", data)

@login_required
def departments(request):
    departments = Department.objects.filter(company=request.user.buyer_profile.company)
    department_form = DepartmentForm(request.POST or None)
    if request.method == "POST":
        if department_form.is_valid():
            department = department_form.save(commit=False)
            department.company = request.user.buyer_profile.company
            department.save()
            messages.success(request, 'Department added successfully')
            return redirect('departments')
        else:
            messages.error(request, 'Error. Department list not updated.')
    data = {
        'departments': departments,
        'department_form': department_form,
        'table_headers': ['Name']
    }
    return render(request, "settings/departments.html", data)

@login_required
def account_codes(request):
    account_codes = AccountCode.objects.filter(company=request.user.buyer_profile.company)    
    account_code_form = AccountCodeForm(request.POST or None)
    account_code_form.fields['departments'].queryset = Department.objects.filter(company=request.user.buyer_profile.company)
    if request.method == "POST":
        if account_code_form.is_valid():
            code = account_code_form.save(commit=False)
            code.company = request.user.buyer_profile.company
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
def products(request):
    products = CatalogItem.objects.filter(buyer_co=request.user.buyer_profile.company)
    product_form = CatalogItemForm(request.POST or None)
    product_form.fields['category'].queryset = Category.objects.filter(buyer_co=request.user.buyer_profile.company)
    product_form.fields['vendor_co'].queryset = VendorCo.objects.filter(buyer_co=request.user.buyer_profile.company)    
    if request.method == "POST":
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.currency = product.vendor_co.currency
            product.buyer_co = request.user.buyer_profile.company
            product.save()
            messages.success(request, "Product added successfully")
            return redirect('products')
        else:
            messages.error(request, 'Error. Catalog list not updated.')
    currency = request.user.buyer_profile.company.currency.upper()
    data = {
        'products': products,
        'product_form': product_form,
        'table_headers': ['Name', 'SKU', 'Description', 'Price ('+currency+')', 'Unit', 'Category', 'Vendor'],
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
        'table_headers': ['Co. Name']
    }
    return render(request, "settings/vendors.html", data)    

@login_required
def view_vendor(request, vendor_id, vendor_name):
    vendor = VendorCo.objects.filter(pk=vendor_id)
    company = Company.objects.filter(pk=vendor_id)    
    try:
        location = Location.objects.filter(company=company)
        data = serialize('json', list(vendor) + list(company) + list(location))
    except TypeError: # No Location has been determined for Vendor
        data = serialize('json', list(vendor) + list(company))
    return HttpResponse(data, content_type='application/json')

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
    try:
        billing_add = Location.objects.filter(company=buyer.company, loc_type='Billing').first()
        billing_address_form = LocationForm(request.POST or None, instance=billing_add)
    except ObjectDoesNotExist:
        billing_address_form = LocationForm(request.POST or None)
    try:
        shipping_add = Location.objects.filter(company=buyer.company, loc_type='Shipping').first()
        shipping_address_form = LocationForm(request.POST or None, instance=shipping_add)
    except:    
        shipping_address_form = LocationForm(request.POST or None)

    # pdb.set_trace()
    if request.method == "POST":
        if 'company' in request.POST:
            if company_form.is_valid():
                company_form.save()
                messages.success(request, "Company profile updated successfully")
                return redirect('company_profile')
        elif 'billing' in request.POST:
            if billing_address_form.is_valid():
                billing_add = billing_address_form.save(commit=False)
                billing_add.company=buyer.company
                billing_add.save()
                messages.success(request, "Billing address updated successfully")
                return redirect('company_profile')
        elif 'shipping' in request.POST:
            if shipping_address_form.is_valid():
                shipping_add = shipping_address_form.save(commit=False)
                shipping_add.company=buyer.company
                shipping_add.save()
                messages.success(request, "Shipping address updated successfully")
                return redirect('company_profile')         
        else:
            messages.error(request, 'Error. Settings not updated')        
    data = {
        'company_form': company_form,
        'billing_address_form': billing_address_form,
        'shipping_address_form': shipping_address_form
    }
    return render(request, "settings/company_profile.html", data)       

@login_required
def new_requisition(request): 
    buyer = request.user.buyer_profile
    requisition_form = RequisitionForm(request.POST or None,
                                       initial= {'number': "RO"+str(Requisition.objects.filter(buyer_co=buyer.company).count()+1)})    
    OrderItemFormSet = inlineformset_factory(parent_model=Requisition, model=OrderItem, form=OrderItemForm, extra=1)
    orderitem_formset = OrderItemFormSet(request.POST or None)
    initialize_newreq_forms(request.user, requisition_form, orderitem_formset)    
    
    if request.method == "POST":
        if requisition_form.is_valid() and orderitem_formset.is_valid():
            requisition = save_new_requisition(buyer, requisition_form)
            save_newreq_orderitems(requisition, orderitem_formset)
            save_newreq_statuses(buyer, requisition)
            messages.success(request, 'Requisition submitted successfully')
            return redirect('new_requisition')
        else:
            messages.error(request, 'Error. Requisition not submitted')
    data = {
        'requisition_form': requisition_form,
        'orderitem_formset': orderitem_formset,
        'table_headers': ['Product', 'Quantity', 'Account Code', 'Comments'],
    }
    return render(request, "requests/new_requisition.html", data)


@login_required()
def requisitions(request):
    buyer = request.user.buyer_profile
    requisitions = Requisition.objects.filter(buyer_co=buyer.company)
    # pdb.set_trace()
    all_requisitions, pending_requisitions, approved_requisitions, denied_requisitions = get_requisitions(requisitions)    
    data = {
        'all_requisitions': all_requisitions,
        'pending_requisitions': pending_requisitions,
        'approved_requisitions': approved_requisitions,
        'denied_requisitions': denied_requisitions,
    }
    return render(request, "requests/requisitions.html", data)

@login_required
def view_requisition(request, requisition_id):
    buyer = request.user.buyer_profile
    requisition = Requisition.objects.get(pk=requisition_id)
    # Manage approving/denying requisitions
    if request.method == 'POST':
        if 'approve' in request.POST:
            DocumentStatus.objects.create(value='Approved', author=buyer, document=requisition)
            for order_item in requisition.order_items.all():
                OrderItemStatus.objects.create(value='Approved', author=buyer, order_item=order_item)
            messages.success(request, 'Requisition approved')
        if 'deny' in request.POST:
            DocumentStatus.objects.create(value='Denied', author=buyer, document=requisition)
            for order_item in requisition.order_items.all():
                OrderItemStatus.objects.create(value='Denied', author=buyer, order_item=order_item)
            messages.success(request, 'Requisition denied')
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
    requisition = Requisition.objects.get(pk=requisition_id)
    data = {
        'requisition': requisition,        
    }
    return render(request, "requests/print_requisition.html", data)

@login_required
def new_purchaseorder(request):
    buyer = request.user.buyer_profile
    all_items = OrderItem.objects.filter(requisition__buyer_co=buyer.company).exclude(purchase_order__isnull=False)
    approved_order_items = all_items.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Approved')
    po_form = PurchaseOrderForm(request.POST or None,
                                initial= {'number': "PO"+str(PurchaseOrder.objects.filter(buyer_co=buyer.company).count()+1)})
    po_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company)
    po_form.fields['billing_add'].queryset = Location.objects.filter(company=buyer.company)
    po_form.fields['shipping_add'].queryset = Location.objects.filter(company=buyer.company)
    po_form.fields['vendor_co'].queryset = VendorCo.objects.filter(buyer_co=buyer.company)
    if request.method == 'POST':
        if po_form.is_valid():
            purchase_order = po_form.save(commit=False)
            purchase_order.preparer = buyer
            purchase_order.currency = buyer.company.currency
            purchase_order.date_issued = timezone.now()
            purchase_order.buyer_co = buyer.company
            purchase_order.sub_total = 0
            purchase_order.save()
            DocumentStatus.objects.create(value='Open', author=buyer, document=purchase_order)

            item_ids = request.POST.getlist('order_items')
            items = OrderItem.objects.filter(id__in=item_ids)
            for item in items:
                item.purchase_order = purchase_order          
                item.save()
                OrderItemStatus.objects.create(value='Ordered', author=buyer, order_item=item)
                purchase_order.sub_total += item.sub_total
            purchase_order.grand_total = purchase_order.sub_total + purchase_order.cost_shipping + purchase_order.cost_other + purchase_order.tax_amount - purchase_order.discount_amount
            purchase_order.save()
            messages.success(request, 'PO created successfully')
            return redirect('purchaseorders')  
        else:
            messages.error(request, 'Error. Purchase order not created')
    currency = buyer.company.currency
    data = {
        'approved_order_items': approved_order_items,
        'po_form': po_form,
        'currency': currency,
        'item_header': ['', 'Order No.', 'Item', 'Quantity', 'Vendor', 'Date Required', 'Total Cost ('+currency+')'],
        'po_header': ['Item', 'Qty', 'Vendor', 'Total Cost ('+currency+')', ''],
    }
    return render(request, "pos/new_purchaseorder.html", data)

@login_required
def purchaseorders(request):
    buyer = request.user.buyer_profile
    pos = PurchaseOrder.objects.filter(buyer_co=buyer.company)
    all_pos, open_pos, closed_pos, cancelled_pos, paid_pos = get_pos(pos)
    data = {
        'all_pos': all_pos,
        'open_pos': open_pos,
        'closed_pos': closed_pos,
        'cancelled_pos': cancelled_pos,
        'paid_pos': paid_pos,
        'po_table_template': '_includes/po_table.html',
        'href': 'view_purchaseorder',
        'title': 'Purchase Orders',
    }
    return render(request, "pos/purchaseorders.html", data)

@login_required
def print_purchaseorder(request, po_id):
    purchase_order = PurchaseOrder.objects.get(pk=po_id)
    data = {
        'purchase_order': purchase_order,        
    }
    return render(request, "pos/print_purchaseorder.html", data)

@login_required
def view_purchaseorder(request, po_id):
    buyer = request.user.buyer_profile
    purchase_order = PurchaseOrder.objects.get(pk=po_id)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            DocumentStatus.objects.create(value='Cancelled', author=buyer, document=purchase_order)
            for order_item in purchase_order.order_items.all():
                OrderItemStatus.objects.create(value='Cancelled', author=buyer, order_item=order_item)
            messages.success(request, 'PO Cancelled')
        else:
            messages.error(request, 'Error. PO not updated')
        return redirect('purchaseorders')
    data = {
        'purchase_order': purchase_order,
    }
    return render(request, "pos/view_purchaseorder.html", data)

@login_required
def receive_pos(request):
    pos = PurchaseOrder.objects.filter(buyer_co=request.user.buyer_profile.company)
    all_pos, open_pos, closed_pos, cancelled_pos, paid_pos = get_pos(pos)
    data = {
        'all_pos': all_pos,
        'open_pos': open_pos,
        'closed_pos': closed_pos,
        'cancelled_pos': cancelled_pos,
        'paid_pos': paid_pos,
        'po_table_template': '_includes/po_table.html',
        'href': 'receive_purchaseorder',
        'title': 'Receive Purchase Orders',
    }
    return render(request, "pos/receive_pos.html", data)

@login_required
def receive_purchaseorder(request, po_id):
    buyer = request.user.buyer_profile
    purchase_order = PurchaseOrder.objects.get(pk=po_id)
    if request.method == 'POST':
        item_ids = request.POST.getlist('order_items')
        approved_items = OrderItem.objects.filter(id__in=item_ids)
        try:
            for item in approved_items:
                OrderItemStatus.objects.create(value='Delivered', author=buyer, order_item=item)
            all_items = OrderItem.objects.filter(purchase_order=purchase_order)
            unapproved_order_items = all_items.annotate(latest_update=Max('status_updates__date')).filter(~Q(status_updates__value='Delivered'))    
            if len(unapproved_order_items) == 0:            
                DocumentStatus.objects.create(value='Closed', author=buyer, document=purchase_order)
            messages.success(request, 'Orders updated successfully')            
            return redirect('receive_pos')
        except:
            messages.error(request, 'Error updating items')        
    data = {
        'purchase_order': purchase_order,
    }
    return render(request, "pos/receive_purchaseorder.html", data)

@login_required
def po_orderitems(request, po_id):
    purchase_order = PurchaseOrder.objects.get(pk=po_id)
    buyer_co = request.user.buyer_profile.company
    try:
        # Get relevant PO orderItems and serialize the data into json for ajax request
        order_items = OrderItem.objects.filter(purchase_order=purchase_order)
        data = OrderItemSerializer(order_items, many=True).data
    except TypeError:
        data = []
    return HttpResponse(JSONRenderer().render(data), content_type='application/json')

@login_required
def new_invoice(request):
    buyer = request.user.buyer_profile
    currency = buyer.company.currency
    invoice_form = InvoiceForm(request.POST or None,
                                initial= {'number': "INV"+str(Invoice.objects.filter(buyer_co=buyer.company).count()+1)})
    invoice_form.fields['vendor_co'].queryset = VendorCo.objects.filter(buyer_co=buyer.company)
    # TODO: POs with UNBILLED ITEMS ONLY 
    invoice_form.fields['purchase_order'].queryset = PurchaseOrder.objects.filter(buyer_co=buyer.company)
    file_form = FileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        file_form = FileForm(request.POST, request.FILES)
        if invoice_form.is_valid() and file_form.is_valid():            
            invoice = invoice_form.save(commit=False)       
            invoice.preparer = request.user.buyer_profile
            invoice.currency = request.user.buyer_profile.company.currency
            invoice.buyer_co = request.user.buyer_profile.company
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
            DocumentStatus.objects.create(value='Closed', author=buyer, document=purchase_order)
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
    invoices = Invoice.objects.filter(buyer_co=buyer.company)
    all_invoices, pending_invoices, approved_invoices, cancelled_invoices, paid_invoices = get_invoices(invoices)
    data = {
        'all_invoices': all_invoices,
        'pending_invoices': pending_invoices,
        'approved_invoices': approved_invoices,
        'cancelled_invoices': cancelled_invoices,
        'paid_invoices': paid_invoices,
        'table_headers': ['Invoice No.', 'Amount ('+buyer.company.currency+')', 'Invoice Created', 'Date Due', 'Vendor', 'PO No.', 'File', 'Comments']
    }
    return render(request, "invoices/invoices.html", data)

@login_required
def print_invoice(request, invoice_id):
    invoice = Invoice.objects.get(pk=invoice_id)
    data = {
        'invoice': invoice,        
    }
    return render(request, "invoices/print_invoice.html", data)

@login_required
def view_invoice(request, invoice_id):
    buyer = request.user.buyer_profile
    invoice = Invoice.objects.get(pk=invoice_id)
    if request.method == 'POST':
        if 'paid' in request.POST:
            DocumentStatus.objects.create(value='Paid', author=buyer, document=invoice)
            for order_item in invoice.order_items.all():
                OrderItemStatus.objects.create(value='Paid', author=buyer, order_item=order_item)
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
    vendor_co = VendorCo.objects.get(pk=vendor_id)    
    try:
        purchase_orders = PurchaseOrder.objects.filter(buyer_co=buyer_co, vendor_co=vendor_co)
        po_numbers = [order.number for order in purchase_orders]
        documents = Document.objects.filter(number__in=po_numbers)
        data = serialize('json', list(documents))
    except TypeError:
        pass
    return HttpResponse(data, content_type='application/json')

@login_required
def inventory(request):
    buyer = request.user.buyer_profile
    all_items = OrderItem.objects.filter(requisition__buyer_co=buyer.company)
    # TODO: CUSTOM MANAGER TO GET LATEST STATUS IN QUERYSET
    delivered_order_items = all_items.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Delivered')
    inventory_count = delivered_order_items.values('product__name', 'product__category__name').annotate(totalCount=Sum('quantity'))
    data = {
        'inventory_count': inventory_count,
    }
    return render(request, "invoices/inventory.html", data)