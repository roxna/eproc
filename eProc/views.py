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
from django.utils import timezone
from django.utils.http import is_safe_url
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
            department = Department.objects.create(name='Admin', company=company)
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

####################################
###         MAIN PAGES           ### 
####################################

def thankyou(request):
    return render(request, 'registration/thankyou.html')

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
            ['new_purchaseorder','1. Create a purchase order', po_exists],
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
    
    requisitions = Requisition.objects.filter(buyer_co=buyer.company)
    all_requisitions, pending_requisitions, approved_requisitions, closed_requisitions, paid_requisitions, cancelled_requisitions, denied_requisitions = get_documents(buyer, requisitions)
    
    pos = PurchaseOrder.objects.filter(buyer_co=buyer.company)
    all_pos, pending_pos, approved_pos, closed_pos, paid_pos, cancelled_pos, denied_pos = get_documents(buyer, pos)
    # pending_requisitions = requisitions.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Pending')
    # pending_pos = pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Pending')
    
    all_items = OrderItem.objects.filter(requisition__buyer_co=buyer.company)    
    items_received = all_items.annotate(latest_update=Max('status_updates__date')).filter(Q(status_updates__value='Delivered Complete') | Q(status_updates__value='Delivered Partial'))

    dept_spend = items_received.values('requisition__department__name').annotate(total_cost=Sum(F('quantity')*F('unit_price'), output_field=models.DecimalField()))
    categ_spend = items_received.values('product__category__name').annotate(total_cost=Sum(F('quantity')*F('unit_price'), output_field=models.DecimalField()))
    product_spend = items_received.values('product__name').annotate(total_cost=Sum(F('quantity')*F('unit_price'), output_field=models.DecimalField()))
    data = {
        'pending_req_count': len(pending_requisitions),
        'pending_po_count': len(pending_pos),
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
def settings(request):
    return render(request, "settings/settings.html")

@login_required
def users(request):    
    buyer = request.user.buyer_profile
    # user_form = AddUserForm(request.POST or None)
    # buyer_profile_form = BuyerProfileForm(request.POST or None)
    # buyer_profile_form.fields['department'].queryset = Department.objects.filter(company=buyer.company)
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
            if location_form.is_valid():
                save_location(location_form, buyer)
                messages.success(request, 'Location updated successfully')
        elif 'add_User' in request.POST:
            if user_form.is_valid() and buyer_profile_form.is_valid():                
                save_user(user_form, buyer_profile_form, company, location)                
                send_verific_email(user, user.id*settings.SCALAR)
                messages.success(request, 'User successfully invited')
            else:
                messages.error(request, 'Error adding user. Please try again.')
        elif 'add_Department' in request.POST:
            if department_form.is_valid():
                save_department(department_form, buyer, location)                
                messages.success(request, 'Department added successfully')
            else:
                messages.error(request, 'Error. Department not added.')  
        else:
            pass
    data = {
        'location': location,
        'location_form': location_form,
        
        'buyers': buyers,
        'user_form': user_form,
        'buyer_profile_form': buyer_profile_form,
        'user_table_headers': ['Username', 'Email', 'Role', 'Status'],

        'departments': departments,
        'department_form': department_form,
        'dept_table_headers': ['Name'],        
    }
    return render(request, "settings/view_location.html", data)

@login_required
def account_codes(request):
    buyer = request.user.buyer_profile
    account_codes = AccountCode.objects.filter(company=request.user.buyer_profile.company)    
    account_code_form = AccountCodeForm(request.POST or None)
    account_code_form.fields['departments'].queryset = Department.objects.filter(company=buyer.company)
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

@login_required
def new_requisition(request): 
    buyer = request.user.buyer_profile
    requisition_form = RequisitionForm(request.POST or None,
                                       initial= {'number': "RO"+str(Requisition.objects.filter(buyer_co=buyer.company).count()+1)})    
    requisition_form.fields['department'].queryset = Department.objects.filter(company=buyer.company)
    requisition_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(department=buyer.department, role__in=['Approver', 'SuperUser']).exclude(user=request.user)    
    OrderItemFormSet = inlineformset_factory(parent_model=Requisition, model=OrderItem, form=OrderItemForm, extra=1)
    orderitem_formset = OrderItemFormSet(request.POST or None)
    initialize_newreq_forms(request.user, requisition_form, orderitem_formset)    
    
    if request.method == "POST":
        if requisition_form.is_valid() and orderitem_formset.is_valid():
            requisition = save_new_document(buyer, requisition_form)
            # Save order_items and OrderItemsStatus --> see utils.py
            save_orderitems(requisition, orderitem_formset)
            save_newreq_statuses(buyer, requisition)
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


@login_required()
def requisitions(request):
    buyer = request.user.buyer_profile
    requisitions = Requisition.objects.filter(buyer_co=buyer.company)
    # Returns relevant requisitions based on their status and the buyer's authorization to see them (see utils.py)
    all_requisitions, pending_requisitions, approved_requisitions, closed_requisitions, paid_requisitions, cancelled_requisitions, denied_requisitions = get_documents(buyer, requisitions)
    data = {
        'all_requisitions': all_requisitions,
        'pending_requisitions': pending_requisitions,
        'approved_requisitions': approved_requisitions,
        'denied_requisitions': denied_requisitions,
        'cancelled_requisitions': cancelled_requisitions,
    }
    return render(request, "requests/requisitions.html", data)

@login_required
def view_requisition(request, requisition_id):
    buyer = request.user.buyer_profile
    requisition = get_object_or_404(Requisition, pk=requisition_id)
    # Manage approving/denying requisitions
    if request.method == 'POST':
        if 'approve' in request.POST:
            DocumentStatus.objects.create(value='Approved', author=buyer, document=requisition)
            for order_item in requisition.order_items.all():
                OrderItemStatus.objects.create(value='Pending', author=buyer, order_item=order_item)
            messages.success(request, 'Requisition approved')
        elif 'deny' in request.POST:
            DocumentStatus.objects.create(value='Denied', author=buyer, document=requisition)
            for order_item in requisition.order_items.all():
                OrderItemStatus.objects.create(value='Denied', author=buyer, order_item=order_item)
            messages.success(request, 'Requisition denied')
        elif 'cancel' in request.POST:
            DocumentStatus.objects.create(value='Cancelled', author=buyer, document=requisition)
            for order_item in requisition.order_items.all():
                OrderItemStatus.objects.create(value='Cancelled', author=buyer, order_item=order_item)
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

@login_required
def new_purchaseorder(request):
    buyer = request.user.buyer_profile
    all_items = OrderItem.objects.filter(requisition__buyer_co=buyer.company).exclude(purchase_order__isnull=False)
    approved_order_items = all_items.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Approved')
    po_form = PurchaseOrderForm(request.POST or None,
                                initial= {'number': "PO"+str(PurchaseOrder.objects.filter(buyer_co=buyer.company).count()+1)})    
    initialize_newpo_forms(buyer, po_form)
    if request.method == 'POST':
        if po_form.is_valid():
            purchase_order = save_new_document(buyer, po_form)
            DocumentStatus.objects.create(value='Pending', author=buyer, document=purchase_order)

            item_ids = request.POST.getlist('order_items')
            items = OrderItem.objects.filter(id__in=item_ids)
            for item in items:
                item.purchase_order = purchase_order          
                item.save()
                OrderItemStatus.objects.create(value='Approved', author=buyer, order_item=item)
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
        'po_header': ['Item', 'Qty', 'Unit Price', 'Total Cost ('+currency+')', 'Vendor',],
    }
    return render(request, "pos/new_purchaseorder.html", data)

@login_required
def purchaseorders(request):
    buyer = request.user.buyer_profile
    pos = PurchaseOrder.objects.filter(buyer_co=buyer.company)
    all_pos, pending_pos, approved_pos, closed_pos, paid_pos, cancelled_pos, denied_pos = get_documents(buyer, pos)
    data = {
        'all_pos': all_pos,
        'pending_pos': pending_pos,
        'approved_pos': approved_pos,
        'closed_pos': closed_pos,        
        'paid_pos': paid_pos,
        'cancelled_pos': cancelled_pos,
        'denied_pos': denied_pos,
        'currency': buyer.company.currency,
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
        if 'approve' in request.POST:
            DocumentStatus.objects.create(value='Approved', author=buyer, document=purchase_order)
            for order_item in purchase_order.order_items.all():
                OrderItemStatus.objects.create(value='Approved', author=buyer, order_item=order_item)
            messages.success(request, 'Purchase Order approved')
        elif 'deny' in request.POST:
            DocumentStatus.objects.create(value='Denied', author=buyer, document=purchase_order)
            for order_item in purchase_order.order_items.all():
                OrderItemStatus.objects.create(value='Denied', author=buyer, order_item=order_item)
            messages.success(request, 'Purchase Order denied')
        elif 'cancel' in request.POST:
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
    buyer = request.user.buyer_profile
    pos = PurchaseOrder.objects.filter(buyer_co=buyer.company)
    all_pos, pending_pos, approved_pos, closed_pos, paid_pos, cancelled_pos, denied_pos = get_documents(buyer, pos)
    data = {
        'approved_pos': approved_pos,
        'currency': buyer.company.currency,
        'href': 'receive_purchaseorder',
    }
    return render(request, "pos/receive_pos.html", data)

@login_required
def receive_purchaseorder(request, po_id):
    buyer = request.user.buyer_profile
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
    ReceivePOFormSet = inlineformset_factory(PurchaseOrder, OrderItem, ReceivePOForm, extra=0)
    receive_po_formset = ReceivePOFormSet(request.POST or None, instance=purchase_order)

    if request.method == 'POST':
        if 'close' in request.POST:
            DocumentStatus.objects.create(value='Closed', author=buyer, document=purchase_order)
            messages.success(request, 'Purchase Order closed')
        elif 'save' in request.POST:
            for index, form in enumerate(receive_po_formset.forms):
                if form.is_valid() and form.has_changed():
                    quantity = form.cleaned_data['quantity']
                    qty_delivered = form.cleaned_data['qty_delivered']
                    qty_returned = form.cleaned_data['qty_returned']
                    if qty_delivered > quantity or qty_returned > quantity:
                        messages.error(request, 'Error. Quantity delivered/returned must be less than quantity requested.')
                    elif qty_delivered + qty_returned == quantity:
                        item = form.save()
                        OrderItemStatus.objects.create(value='Delivered Complete', author=buyer, order_item=item)
                        messages.success(request, 'Orders updated successfully')
                    else:
                        item = form.save()
                        OrderItemStatus.objects.create(value='Delivered Partial', author=buyer, order_item=item)
                        messages.success(request, 'Orders updated successfully')
        else:
            messages.error(request, 'Error updating items')        
        return redirect('receive_pos')
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
    invoices = Invoice.objects.filter(buyer_co=buyer.company)
    all_invoices, pending_invoices, approved_invoices, closed_invoices, paid_invoices, cancelled_invoices, denied_invoices = get_documents(buyer, invoices)
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
    print delivered_count
    print drawndown_count
    # Chain/combine the two querysets into a list, not another Queryset (can't use annotate etc)
    # TypeError for empty list
    try:
        inventory_list = list(chain(delivered_count, neg_drawndown_count)) 
    except TypeError:
        inventory_list = []

    # print inventory_list
    # Convert list of dictionaries to dictionary
    # inventory_dict = defaultdict(int)
    # for item in inventory_list:
    #     inventory_dict[item['product__name']] += item['total_qty']
    
    # Convert dictionary back to list of dicts
    # inventory_count = [{'product__name': prod, 'total_qty': qty} for prod, qty in inventory_dict.items()]

    data = {
        'location': location,
        'inventory_list': inventory_list,
        # 'inventory_count': inventory_count,

        'delivered_list': delivered_list,
        # 'delivered_count': delivered_count,

        'drawndown_list': drawndown_list,
        # 'drawndown_count': drawndown_count,
    }
    return render(request, "inventory/inventory_location.html", data)


@login_required
def new_drawdown(request):
    buyer = request.user.buyer_profile
    drawdown_form = DrawdownForm(request.POST or None,
                                       initial= {'number': 'DD'+str(Drawdown.objects.filter(buyer_co=buyer.company).count()+1)})
    DrawdownItemFormSet = inlineformset_factory(parent_model=Drawdown, model=OrderItem, form=DrawdownItemForm, extra=1)
    drawdownitem_formset = DrawdownItemFormSet(request.POST or None)
    initialize_newdrawdown_forms(request.user, drawdown_form, drawdownitem_formset)    
    
    if request.method == "POST":
        if drawdown_form.is_valid() and drawdownitem_formset.is_valid():
            drawdown = save_new_document(buyer, drawdown_form)
            save_orderitems(drawdown, drawdownitem_formset)
            save_newdrawdown_statuses(buyer, drawdown)
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
            DocumentStatus.objects.create(value='Approved', author=buyer, document=drawdown)
            for order_item in drawdown.order_items.all():
                OrderItemStatus.objects.create(value='Drawdown Approved', author=buyer, order_item=order_item)
            messages.success(request, 'Drawdown Approved')
        elif 'deny' in request.POST:
            DocumentStatus.objects.create(value='Denied', author=buyer, document=drawdown)
            for order_item in drawdown.order_items.all():
                OrderItemStatus.objects.create(value='Drawdown Denied', author=buyer, order_item=order_item)
            messages.success(request, 'Drawdown Denied')     
        elif 'cancel' in request.POST:
            DocumentStatus.objects.create(value='Cancelled', author=buyer, document=drawdown)
            for order_item in drawdown.order_items.all():
                OrderItemStatus.objects.create(value='Drawdown Cancelled', author=buyer, order_item=order_item)
            messages.success(request, 'Drawdown Cancelled')                        
        else:
            messages.error(request, 'Error. Drawdown not updated')
        return redirect('drawdowns')
    data = {
        'drawdown': drawdown,
    }
    return render(request, "inventory/view_drawdown.html", data)

@login_required
def drawdowns(request):
    buyer = request.user.buyer_profile    
    drawdowns = Drawdown.objects.filter(buyer_co=buyer.company)
    all_drawdowns, pending_drawdowns, approved_drawdowns, closed_drawdowns, paid_drawdowns, cancelled_drawdowns, denied_drawdowns = get_documents(buyer, drawdowns)

    data = {
        'all_drawdowns': all_drawdowns,
        'pending_drawdowns': pending_drawdowns,
        'approved_drawdowns': approved_drawdowns,
        'denied_drawdowns': denied_drawdowns,
        'cancelled_drawdowns': cancelled_drawdowns,
        'table_headers': ['Drawdown No.', 'Date Requested', 'Comments']
    }
    return render(request, "inventory/drawdowns.html", data)
