from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login as auth_login
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Max
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
from eProc.models import *
from eProc.forms import *
import csv
import pdb

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=LoginForm,
          current_app=None, extra_context=None):
    redirect_to = request.POST.get(redirect_field_name, '')
    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            auth_login(request, form.get_user())
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)
    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)

def register(request):
    return render(request, "registration/register.html")

@login_required()
def dashboard(request):
    data = {

    }
    return render(request, "dashboard.html", data)

# to register & activate: https://github.com/JunyiJ/django-register-activate/blob/master/register_activate/views.py
@login_required
def users(request):    
    user_form = UserForm(request.POST or None)
    buyer_profile_form = BuyerProfileForm(request.POST or None)                
    if request.method == "POST":
        # pdb.set_trace()
        if request.POST.get('add'):
            if user_form.is_valid() and buyer_profile_form.is_valid():
                user = user_form.save()
                buyer_profile = buyer_profile_form.save(commit=False)
                buyer_profile.user = user
                buyer_profile.company = request.user.buyer_profile.company
                buyer_profile.save()
                messages.success(request, 'User successfully invited')

                # text_content = 'Hey {}, \n\n Welcome to LezzGo! We are excited to have you be a part of our family. \n\n Let us know if we can answer any questions as you book or offer out your first ride. \n\n From the folks at LezzGo!'.format(user.first_name)
                # html_content = '<h2>{}, Welcome to LezzGo!</h2> <div>We are excited to have you be a part of our family.</div><br><div>Let us know if we can answer any questions as you book or offer out your first ride.</div><br><div> Folks at LezzGo!</div>'.format(user.first_name)
                # msg = EmailMultiAlternatives("Welcome to LezzGo!!", text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
                # msg.attach_alternative(html_content, "text/html")
                # msg.send()
                return redirect('users')
        elif request.POST.get('delete'):
            for key in request.POST:
                if key == 'delete':
                    user_id = int(request.POST[key])
                    deleted_user = BuyerProfile.objects.get(pk=user_id)
                    deleted_user.delete()
                    messages.success(request, 'User ' + deleted_user.user.username + ' successfully deleted')
                    return redirect('users')
        else:            
            messages.error(request, 'Error. Please try again')
            return redirect('users')
    users = BuyerProfile.objects.filter(company=request.user.buyer_profile.company)
    data = {
        'users': users,
        'user_form': user_form,
        'buyer_profile_form': buyer_profile_form,
        'table_headers': ['Username', 'Email Address', 'Role', ' ',]
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
def products(request):
    products = CatalogItem.objects.filter(buyerCo=request.user.buyer_profile.company)
    product_form = CatalogItemForm(request.POST or None)
    product_form.fields['category'].queryset = Category.objects.filter(buyerCo=request.user.buyer_profile.company)
    product_form.fields['vendorCo'].queryset = VendorCo.objects.filter(buyer_co=request.user.buyer_profile.company)
    if request.method == "POST":
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.buyerCo = request.user.buyer_profile.company
            product.save()
            messages.success(request, "Product added successfully")
            return redirect('products')
        else:
            messages.error(request, 'Error. Catalog list not updated.')
    data = {
        'products': products,
        'product_form': product_form,
        'table_headers': ['Name', 'SKU', 'Description', 'Price', 'Category', 'Vendor'],
    }
    return render(request, "settings/catalog.html", data)

@login_required
def upload_product_csv(request):
    csv_form = UploadCSVForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if csv_form.is_valid():
            csv_file = request.FILES['file'].read()
            reader = csv.reader(csv_file, delimiter=',')
            header = next(reader) #Ignore header row
            if sum(1 for row in reader) < 2:  #Check there's at least one line item to upload
                messages.error(request, 'Error. Please make sure you have data correctly entered.')
            try:
                buyerCo = request.user.buyer_profile.company
                for row in reader: 
                    name = row[0]
                    desc = row[1]
                    sku = row[2]
                    unit_price = float(row[3])
                    unit_type = row[4]
                    currency = row[5]
                    category, categ_created = Category.objects.get_or_create(name=row[6], buyerCo=buyerCo)
                    vendorCo, vendorCo_created = VendorCo.objects.get_or_create(name=row[7], buyer_co=buyerCo)
                    CatalogItem.objects.create(name=name, desc=desc, sku=sku, unit_price=unit_price, unit_type=unit_type, currency=currency, vendorCo=vendorCo, buyerCo=buyerCo)
                messages.success(request, 'Products successfully uploaded.')
            except:
                messages.error(request, 'Error in uploading the file. Please try again.')
    data = {
    'csv_form': csv_form,
    }
    return render(request, "settings/catalog_import.html", data)

# DONE
@login_required
def vendors(request):
    vendors = VendorCo.objects.filter(buyer_co=request.user.buyer_profile.company)
    vendor_form = VendorForm(request.POST or None)
    location_form = LocationForm(request.POST or None)
    vendor_profile_form = VendorForm(request.POST or None)
    if request.method == "POST":
        if vendor_form.is_valid() and location_form.is_valid():
            vendor = vendor_form.save()
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
        'vendor_profile_form': vendor_profile_form,
        'table_headers': ['Vendor Name']
    }
    return render(request, "settings/vendors.html", data)    

@login_required
def upload_vendor_csv(request):
    csv_form = UploadCSVForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if csv_form.is_valid():
            csv_file = request.FILES['file'].read()
            reader = csv.reader(csv_file, delimiter=',')
            header = next(reader) #Ignore header row
            if sum(1 for row in reader) < 2:  #Check there's at least one line item to upload
                messages.error(request, 'Error. Please make sure you have data correctly entered.')
            try:
                buyerCo = request.user.buyer_profile.company
                for row in reader: 
                    # co_name = row[0]
                    # co_currency = row[1]
                    # address1 = row[2]
                    # address2 = row[3]
                    # city = row[4]
                    # co_state = row[5]
                    # co_zipcode = row[6]
                    # co_phone = row[7]
                    # co_email = row[8]
                    # username = row[9]
                    # email = row[9]
                    # vendorCo, vendorCo_created = VendorCo.objects.get_or_create(name=row[7], buyer_co=buyerCo)
                    company = VendorCo.objects.create()
                    Location.objects.create(name="Headquarters", is_primary=True, address1=address1, address2=address2, city=city, state=state, country=country, zipcode=zipcode, phone=phone, email=email, company=company)
                    VendorProfile.objects.create()
                messages.success(request, 'Vendor list successfully uploaded.')
            except:
                messages.error(request, 'Error in uploading the file. Please try again.')
    data = {
    'csv_form': csv_form,
    }
    return render(request, "settings/vendor_import.html", data)

# DONE
@login_required
def user_profile(request):
    user_form = UserForm(request.POST or None, instance=request.user)
    buyer_profile = request.user.buyer_profile
    if request.method == "POST":
        if user_form.is_valid():
            user = user_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('user_profile')
        else:
            messages.error(request, 'Error. Profile not updated')
    data = {
        'user_form': user_form,
        'buyer_profile': buyer_profile
    }
    return render(request, "settings/user_profile.html", data)    

# DONE
@login_required
def company_profile(request):
    company_form = CompanyProfileForm(request.POST or None, instance=request.user.buyer_profile.company)
    if request.method == "POST":
        if company_form.is_valid():
            company = company_form.save()
            messages.success(request, "Company settings updated successfully")
            return redirect('company_profile')
        else:
            messages.error(request, 'Error. Settings not updated')        
    data = {
        'company_form': company_form
    }
    return render(request, "settings/company_profile.html", data)       

@login_required
def new_requisition(request):    
    requisition_form = RequisitionForm(request.POST or None,
                                        initial= {'number': "RO"+str(Requisition.objects.filter(buyerCo=request.user.buyer_profile.company).count()+1)})
    requisition_form.fields['department'].queryset = Department.objects.filter(company=request.user.buyer_profile.company)
    requisition_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=request.user.buyer_profile.company).exclude(user=request.user)

    OrderItemFormSet = inlineformset_factory(parent_model=Requisition, model=OrderItem, form=OrderItemForm, extra=1)
    orderitem_formset = OrderItemFormSet(request.POST or None)
    for orderitem_form in orderitem_formset: 
        orderitem_form.fields['product'].queryset = CatalogItem.objects.filter(buyerCo=request.user.buyer_profile.company)
        orderitem_form.fields['account_code'].queryset = AccountCode.objects.filter(company=request.user.buyer_profile.company)
    
    if request.method == "POST":
        if requisition_form.is_valid() and orderitem_formset.is_valid():
            requisition = requisition_form.save(commit=False)
            requisition.preparer = request.user.buyer_profile
            requisition.currency = request.user.buyer_profile.company.currency
            requisition.date_issued = timezone.now()
            requisition.buyerCo = request.user.buyer_profile.company
            requisition.sub_total = 0
            requisition.save()

            # Save the data for each form in the order_items formset 
            for index, orderitem_form in enumerate(orderitem_formset.forms):
                if orderitem_form.is_valid():
                    order_item = orderitem_form.save(commit=False)
                    order_item.number = requisition.number + "-" + str(index+1)
                    order_item.requisition = requisition                    
                    order_item.date_due = requisition.date_due
                    order_item.sub_total = orderitem_form.cleaned_data['product'].unit_price * orderitem_form.cleaned_data['quantity']
                    requisition.sub_total += order_item.sub_total            
                    order_item.save()            
            requisition.save()

            if request.user.buyer_profile.role == 'SuperUser' or request.user.buyer_profile.role == 'Approver':
                status = Status.objects.create(value='Approved', color='Approved', author=request.user.buyer_profile, document=requisition)
            else:
                status = Status.objects.create(value='Pending', color='Pending', author=request.user.buyer_profile, document=requisition)

            messages.success(request, 'Requisition submitted successfully')
            return redirect('new_requisition')
        else:
            messages.error(request, 'Error. Requisition not submitted')
    data = {
        'requisition_form': requisition_form,
        'orderitem_formset': orderitem_formset,
        'table_headers': ['Product', 'Quantity', 'Account Code', 'Comments'],
    }
    return render(request, "orders/new_requisition.html", data)


@login_required()
def requisitions(request):
    all_requisitions = Requisition.objects.filter(buyerCo=request.user.buyer_profile.company)
    pending_requisitions = all_requisitions.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value=2)
    approved_requisitions = all_requisitions.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value=3)
    denied_requisitions = all_requisitions.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value=4)
    data = {
        'all_requisitions': all_requisitions,
        'pending_requisitions': pending_requisitions,
        'approved_requisitions': approved_requisitions,
        'denied_requisitions': denied_requisitions,
    }
    return render(request, "orders/requisitions.html", data)

@login_required
def view_requisition(request, requisition_id):
    requisition = Requisition.objects.get(pk=requisition_id)
    latest_status = requisition.status_updates.latest('date')

    # Manage approving/denying requisitions
    if request.method == 'POST':
        if request.POST.get('approve'):
            Status.objects.create(value='Approved', color="Approved", author=request.user.buyer_profile, document=requisition)
            for order_item in requisition.order_items:
                order_item.is_approved = True
            messages.success(request, 'Requisition approved')
        if request.POST.get('deny'):
            Status.objects.create(value='Denied', color="Denied", author=request.user.buyer_profile, document=requisition)
            messages.success(request, 'Requisition denied')
        else:
            messages.error(request, 'Error. Requisition not updated')
        return redirect('requisitions')
    data = {
    'requisition': requisition,
    'latest_status': latest_status,
    'table_headers': ['Product', 'Quantity', 'Account Code', 'Comments'],
    }
    return render(request, "orders/view_requisition.html", data)

@login_required
def new_purchaseorder(request):
    approved_order_items = OrderItem.objects.filter(requisition__buyerCo=request.user.buyer_profile.company).filter(is_approved=True).exclude(purchase_order__isnull=False)
    po_form = PurchaseOrderForm(request.POST or None,
                                initial= {'number': "PO"+str(PurchaseOrder.objects.filter(buyerCo=request.user.buyer_profile.company).count()+1)})
    po_form.fields['billing_add'].queryset = Location.objects.filter(company=request.user.buyer_profile.company)
    po_form.fields['shipping_add'].queryset = Location.objects.filter(company=request.user.buyer_profile.company)
    po_form.fields['vendorCo'].queryset = VendorCo.objects.filter(buyer_co=request.user.buyer_profile.company)
    if request.method == 'POST':
        if po_form.is_valid():
            purchase_order = po_form.save(commit=False)
            purchase_order.preparer = request.user.buyer_profile
            purchase_order.currency = request.user.buyer_profile.company.currency
            purchase_order.date_issued = timezone.now()
            purchase_order.buyerCo = request.user.buyer_profile.company
            purchase_order.sub_total = 0
            purchase_order.save()
            status = Status.objects.create(value='Open', color="Pending", author=request.user.buyer_profile, document=purchase_order)

            item_ids = request.POST.getlist('order_items[]')
            items = OrderItem.objects.filter(id__in=item_ids)
            for item in items:
                item.purchase_order = purchase_order
                purchase_order.sub_total += item.sub_total
            purchase_order.grand_total = purchase_order.sub_total + purchase_order.cost_shipping + purchase_order.cost_other + purchase_order.tax_amount - purchase_order.discount_amount
            purchase_order.save()
            messages.success(request, 'PO created successfully')
            return redirect('purchaseorders')  
        else:
            messages.error(request, 'Error. Purchase order not created')
            return redirect('new_purchaseorder')
    data = {
        'approved_order_items': approved_order_items,
        'po_form': po_form,
        'currency': request.user.buyer_profile.company.currency,
        'item_header': ['', 'Order No.', 'Item', 'Vendor', 'Date Required', 'Total Cost'],
        'po_header': ['Item', 'Vendor', 'Total Cost'],
    }
    return render(request, "pos/new_purchaseorder.html", data)


@login_required
def purchaseorders(request):
    all_pos = PurchaseOrder.objects.filter(buyerCo=request.user.buyer_profile.company)
    open_pos = all_pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value=5)
    closed_pos = all_pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value=6)
    cancelled_pos = all_pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value=7)
    paid_pos = all_pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value=8)
    data = {
        'all_pos': all_pos,
        'open_pos': open_pos,
        'closed_pos': closed_pos,
        'cancelled_pos': cancelled_pos,
        'paid_pos': paid_pos,
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
    purchase_order = PurchaseOrder.objects.get(pk=po_id)
    latest_status = purchase_order.status_updates.latest('date')
    # pdb.set_trace()
    data = {
        'purchase_order': purchase_order,
        'latest_status': latest_status
    }
    return render(request, "pos/view_purchaseorder.html", data)

