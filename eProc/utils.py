from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Max, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from eProc.forms import *
from eProc.models import *
import stripe


################################
###   PAYMENTS / CHARGES     ### 
################################ 

# Used for method decorator @user_passes_test
def is_subscribed_or_trial_not_over(user):
    return user.is_subscribed() or not user.is_trial_over()

def update_stripe_subscription(user, plan):
    # Stripe Customer & Subscription to 'free' plan created on register
    # Here update Subscription to the selected paid plan
    customer = stripe.Customer.retrieve(user.stripe_customer_id)    
    subscription = stripe.Subscription.retrieve(customer.subscriptions.data[0].id)  #Assuming 1 user - 1 plan
    subscription.plan = plan.identifier
    subscription.save()

# def create_stripe_customer(email, source):
#     return stripe.Customer.create(
#         email=email,
#         source=source,
#     )

# def create_stripe_charge(customer_id, amount, currency, description):
#     return stripe.Charge.create(
#         customer=customer_id,
#         amount=amount,
#         currency=currency,
#         description=description,
#     )

# def create_stripe_subscription(customer_id, plan_identifier):
#     return stripe.Subscription.create(
#           customer=customer_id,
#           plan=plan_identifier,
#         )

################################
###     COMMON METHODS       ### 
################################ 

def send_verific_email(user,random_id):
    text_content = 'Hi {}, \n\n Please click on the following link to activate your account:\nhttp://127.0.0.1:8000/activate/?id={}". \n\n If you have any questions, please reach out at support@eproc.com. \n\n Team at eProc'.format(user.first_name, random_id)
    html_content = '<div>Hi {},</div><br><div>Please click on the following link to activate your account: http://127.0.0.1:8000/activate/?id={}" </div><br><div> If you have any questions, please reach out at support@eproc.com.</div><br><div> Team at eProc</div>'.format(user.first_name, random_id)
    msg = EmailMultiAlternatives("Activate your account", text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# Returns Docs (Reqs/POs etc) where the user is either the preparer OR next_approver, unless user is SuperUser
# User in requisitions, purchaseorders etc in views.py
def get_documents_by_auth(buyer, document_type):
    if buyer.role == 'SuperUser':
        return document_type.objects.filter(buyer_co=buyer.company)
    else:        
        return document_type.objects.filter(preparer=buyer).filter(next_approver=buyer) # .filter().filter() --> either or (vs. filter(x, y))

def get_users_for_notifications(roles, buyer_profile):
    return list(User.objects.filter(Q(buyer_profile__role__in=roles) | Q(buyer_profile=buyer_profile)))


################################
###    INITIALIZE FORMS    ### 
################################ 

def initialize_req_form(buyer, requisition_form, orderitem_formset):
    set_next_approver_not_required(buyer, requisition_form)
    if buyer.role == 'SuperUser':
        # If SuperUser, can select any department and approver, incl. self
        requisition_form.fields['department'].queryset = Department.objects.filter(location__in=buyer.company.get_all_locations())
        requisition_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company, role__in=['Approver', 'SuperUser'])
    else:
        # Else, dept only of buyer's location and next_approver only in buyer's department
        requisition_form.fields['department'].queryset = Department.objects.filter(location=buyer.location)
        requisition_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(department=buyer.department, role__in=['Approver', 'SuperUser']).exclude(user=buyer.user)
    
    for form in orderitem_formset: 
        form.fields['product'].queryset = CatalogItem.objects.filter(buyer_cos=buyer.company)
        form.fields['account_code'].queryset = AccountCode.objects.filter(company=buyer.company)

def initialize_po_form(buyer, po_form):
    po_form.fields['billing_add'].queryset = Location.objects.filter(company=buyer.company)
    po_form.fields['shipping_add'].queryset = Location.objects.filter(company=buyer.company)
    po_form.fields['vendor_co'].queryset = VendorCo.objects.filter(buyer_cos=buyer.company) 

def initialize_invoice_form(buyer, invoice_form):
    invoice_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company, role__in=['Payer', 'SuperUser'])
    set_next_approver_not_required(buyer, invoice_form)

def initialize_drawdown_form(buyer, drawdown_form, drawdownitem_formset):
    drawdown_form.fields['location'].queryset = Location.objects.filter(company=buyer.company)
    set_next_approver_not_required(buyer, drawdown_form)
    if buyer.role == 'SuperUser':
        drawdown_form.fields['department'].queryset = Department.objects.filter(location__company=buyer.company)
        drawdown_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company)        
    else:
        drawdown_form.fields['department'].queryset = Department.objects.filter(location=buyer.location)
        drawdown_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company, role__in=['Inventory Manager', 'Branch Manager', 'SuperUser']).exclude(user=buyer.user)
    
    for drawdownitem_form in drawdownitem_formset: 
        drawdownitem_form.fields['product'].queryset = CatalogItem.objects.filter(buyer_cos=buyer.company)    

def initialize_unbilled_form(buyer, unbilled_formset):
    for form in unbilled_formset:
        form.fields['department'].queryset = Department.objects.filter(location__company=buyer.company)
        form.fields['account_code'].queryset = AccountCode.objects.filter(company=buyer.company)

################################
###   SAVE METHODS - COMMON  ### 
################################ 

# Used by NEW_REQ, NEW_PO, NEW_INVOICE, NEW_DD

# Sets next_approver as not required field if user is SuperUser before is_valid() is called
def set_next_approver_not_required(buyer, form):
    if buyer.role == 'SuperUser':
        form.fields['next_approver'].required = False

def save_new_document(buyer, form):
    document = form.save(commit=False)
    document.preparer = buyer
    document.currency = buyer.company.currency
    document.date_created = timezone.now()
    document.buyer_co = buyer.company
    # Don't save if Invoice - will violate the not-null constraint for invoice.vendor_co etc
    if not isinstance(document, Invoice):
        document.save() 
    return document

def save_vendor(vendor_form, buyer):
    vendor = vendor_form.save()
    vendor.currency = buyer.company.currency
    vendor.buyer_cos.add(buyer.company)
    vendor.save()

# Used by locations and view_location
def save_location(location_form, buyer):
    location = location_form.save(commit=False)
    location.company = buyer.company
    location.save()

# User by view_location (eventually in 'users' too)
def save_user(user_form, buyer_profile_form, company, location):
    user = user_form.save()
    buyer_profile = buyer_profile_form.save(commit=False)
    buyer_profile.user = user              
    buyer_profile.company = company
    buyer_profile.location = location
    buyer_profile.save()
    return user

# User by view_location
def save_department(department_form, buyer, location):
    department = department_form.save(commit=False)
    department.location = location
    department.save() 
    return department

# Updates document and order_item statuses with relevant values/author
def save_status(document, doc_status, item_status, author):
    save_doc_status(document, doc_status, author)
    save_item_status(document, item_status, author)

def save_doc_status(document, doc_status, author):
    document.current_status = status
    document.save()
    DocumentStatus.objects.create(document=document, value=doc_status, author=author)

def save_item_status(document, item_status, author):
    for item in document.items.all():
        if isinstance(document, Drawdown):
            DrawdownItemStatus.objects.create(value=item_status, author=author, item=item)
        else:
            OrderItemStatus.objects.create(value=item_status, author=author, item=item)

def save_file_to_doc(file_form, file_type, file, document):
    file_instance = file_form.save(commit=False)
    file_instance.name = file.name + ' (' + timezone.now().strftime('%Y-%m-%d') + ')'
    file_instance.document = document
    file_instance.save()

def save_notification(text, category, recipients=[], target=None):
    notification = Notification.objects.create(text=text, category=category, target=target)
    for recipient in recipients:
        notification.recipients.add(recipient)


################################
###    SAVE ITEM METHODS     ### 
################################ 
# Save the data for each form in the order_items/drawdown_items formset 

########  REQUISITIONS  ########

# (new_req): Save new_requisition order_items
def save_new_requisition_items(buyer, requisition, formset):
    for index, form in enumerate(formset.forms):
        item = form.save(commit=False)
        item.date_due = requisition.date_due
        item.number = requisition.number + "-" + str(index+1)
        item.requisition = requisition
        item.department = requisition.department
        item.current_status = 'Pending' #OrderItem --> Order PENDING
        if buyer.role == 'SuperUser':
            item.current_status = 'Approved'
            item.qty_approved = item.qty_requested
            item.price_approved = item.price_requested
            item.price_ordered = item.price_approved #Setting this here, will be editable in new_po_confirm
        item.save()

# (view_req): Save items based on approve/deny/cancel
def save_approved_requisition_items(buyer, requisition, formset):
    for form in formset.forms:
        item = form.save()
        item.current_status = 'Approved'
        item.price_ordered = item.price_approved #Setting this here, will be editable in new_po_confirm
        item.save()
    save_status(document=requisition, doc_status='Approved', item_status='Approved', author=buyer)

def save_denied_cancelled_requisition_items(buyer, requisition, formset, status):    
    for form in formset.forms:
        item = form.save()
        item.qty_approved = 0
        item.current_status = status
        if status == 'Denied':
            item.qty_denied = item.qty_requested
        elif status == 'Cancelled':            
            item.qty_cancelled = item.qty_requested
        item.save()
    save_status(document=requisition, doc_status=status, item_status=status, author=buyer)


#######  PURCHASE ORDERS  ########

def save_new_po_items(buyer, purchase_order, formset):
    for form in formset.forms:
        item = form.save(commit=False)
        item.date_due = purchase_order.date_due
        item.purchase_order = purchase_order
        item.current_status = 'Ordered'
        item.save()

# PO marked as Cancelled
# Item back to Approved, PO de-linked
def save_cancelled_po_items(buyer, purchase_order):
    for form in purchase_order.items.all():        
        item.current_status = 'Approved'
        #In case a subset of initial approved items were ordered, not re-setting approved quantity to ordered quantity 
        # will increase approved items beyond the initial number
        item.qty_ordered = 0
        item.comments_ordered = None
        item.purchase_order = None
        item.save()
    save_status(document=requisition, doc_status='Cancelled', item_status='Approved', author=buyer)

def save_received_po_items(buyer, formset):
    for index, form in enumerate(formset.forms):
        if form.has_changed():
            item = form.save()            
            if item.qty_ordered == item.qty_returned:
                item.current_status = 'Returned Completed'
                OrderItemStatus.objects.create(value='Returned', author=buyer, item=item)
            elif item.qty_delivered + item.qty_returned == item.qty_ordered:
                item.current_status = 'Delivered Completed'
                OrderItemStatus.objects.create(value='Delivered', author=buyer, item=item)
            elif item.qty_delivered + item.qty_returned < item.qty_ordered:
                item.current_status = 'Delivered Parial'
                OrderItemStatus.objects.create(value='Delivered', author=buyer, item=item)
            item.save()

#######  UNBILLED ITEMS / SPEND ALLOCATION  ########

def save_spend_allocation_items(buyer, item, formset):
    for form in formset.forms:
        spend_allocation = form.save(commit=False)
        spend_allocation.item = item
        spend_allocation.save()

#######  INVOICES  ########

def save_new_invoice_items(buyer, invoice, items, vendor):
    invoice.vendor_co = vendor
    invoice.save()
    for item in items:                
        invoice.purchase_orders.add(item.purchase_order) # Adding a M2M relationship with PO        
        item.invoice = invoice
        item.save()
    invoice.save()
    DocumentStatus.objects.create(value='Pending', author=buyer, document=invoice)


#######  DRAWDOWNS  ########

# (new_dd)
def save_new_drawdown_items(buyer, drawdown, formset):
    for index, form in enumerate(formset.forms):
        item = form.save(commit=False)
        item.date_due = drawdown.date_due
        item.number = drawdown.number + "-" + str(index+1)
        item.drawdown = drawdown
        item.current_status = 'Pending' #DrawdownItem --> Drawdown PENDING
        if buyer.role == 'SuperUser':
            item.current_status = 'Approved'
            item.qty_approved = item.qty_requested
        item.save()

# (view_dd): Save items based on approve/deny/cancel
def save_approved_dd_items(buyer, drawdown, formset):
    for form in formset.forms:
        item = form.save()
        item.current_status = 'Approved'
        item.save()
    save_status(document=drawdown, doc_status='Approved', item_status='Approved', author=buyer)

def save_denied_cancelled_dd_items(buyer, drawdown, formset, status):    
    for form in formset.forms:
        item = form.save()
        item.qty_approved = 0
        item.current_status = status
        if status == 'Denied':
            item.qty_denied = item.qty_requested
        elif status == 'Cancelled':            
            item.qty_cancelled = item.qty_requested
        item.save()
    save_status(document=drawdown, doc_status=status, item_status=status, author=buyer)


def save_called_dd_items(buyer, formset):
    for form in formset.forms:
        if form.has_changed():
            item = form.save()            
            if item.qty_drawndown == item.qty_approved:
                item.current_status = 'Drawndown Complete'
                DrawdownItemStatus.objects.create(value='Drawndown', author=buyer, item=item)
            elif item.qty_drawndown < item.qty_approved:
                item.current_status = 'Drawndown Parial'
                DrawdownItemStatus.objects.create(value='Drawndown', author=buyer, item=item)
            item.save()
  

################################
###        UPLOAD CSVs       ### 
################################ 

def handle_product_upload(reader, buyer_co):
    for row in reader:
        name = row['PRODUCT_NAME']
        desc = row['DESCRIPTION']
        sku = row['SKU']
        threshold = row['MIN_THRESHOLD']
        unit_price = float(row['UNIT_PRICE'])
        unit_type = row['UNIT_TYPE']
        category, categ_created = Category.objects.get_or_create(name=row['CATEGORY'], buyer_co=buyer_co)
        vendor_co, vendor_created = VendorCo.objects.get_or_create(name=row['VENDOR'], currency=buyer_co.currency)
        vendor_co.buyer_cos.add(buyer_co)
        vendor_co.save()
        product, product_created = CatalogItem.objects.get_or_create(name=name, desc=desc, sku=sku, unit_price=unit_price, unit_type=unit_type, currency=vendor_co.currency, category=category, item_type='Vendor Uploaded', vendor_co=vendor_co)
        product.buyer_cos.add(buyer_co)
        product.save()

def handle_vendor_upload(reader, buyer_co, currency):
    for row in reader:
        name = row['VENDOR_NAME']
        vendorID = row['VENDOR_ID']
        contact_rep = row['CONTACT_PERSON']
        website = row['WEBSITE']
        comments = row['NOTES']
        address1 = row['ADDRESS_LINE1']
        address2 = row['ADDRESS_LINE2']
        city = row['CITY']
        state = row['STATE']
        zipcode = row['ZIP']
        country = row['COUNTRY']
        email = row['EMAIL']
        phone = row['PHONE']     
        vendor_co, vendor_created = VendorCo.objects.get_or_create(name=name, currency=currency, website=website, vendorID=vendorID,
                                                                   contact_rep=contact_rep, comments=comments)
        vendor_co.buyer_cos.add(buyer_co)
        vendor_co.save()
        location = Location.objects.get_or_create(address1=address1, address2=address2, city=city, state=state, zipcode=zipcode, 
                                                  country=country, phone=phone, email=email, company=vendor_co)


################################
###   REPORTS / ANALYSIS     ### 
################################ 
# Get time blocks for spend over time - used by all report views
time_delta = 10 # (in days)

def setup_analysis_data(buyer):
    # Order Items with latest_status = 'Delivered PARTIAL/COMLPETE' (see managers.py) in the requester's department
    items = OrderItem.objects.filter(current_status__in=settings.DELIVERED_STATUSES, requisition__buyer_co=buyer.company)
    period_today, period_mid, period_old, period_end, periods = setup_periods()
    items_by_period = setup_items_by_period(items, period_today, period_mid, period_old, period_end)
    return items, periods, items_by_period

def setup_periods():
    import pytz
    period_today = datetime.now(pytz.utc)
    period_mid = period_today - timedelta(days=time_delta)
    period_old = period_mid - timedelta(days=time_delta)
    period_end = period_old - timedelta(days=time_delta)
    periods = [period_old.strftime("%b %Y"), period_mid.strftime("%b %Y"), period_today.strftime("%b %Y"), ]
    return period_today, period_mid, period_old, period_end, periods

# Filter items based on date of status update
# To change this to based on 'Order' or 'Delivery' date??
def setup_items_by_period(items, period_today, period_mid, period_old, period_end):
    # Order Items with latest_status = 'Delivered PARTIAL/COMLPETE' (see managers.py) in the requester's department    
    items_today = items.filter(Q(status_updates__date__gte=period_mid), Q(status_updates__date__lte=period_today))
    items_mid = items.filter(Q(status_updates__date__gte=period_old), Q(status_updates__date__lte=period_mid))
    items_old = items.filter(Q(status_updates__date__gte=period_end), Q(status_updates__date__lte=period_old))
    items_by_period = [items_old, items_mid, items_today]
    return items_by_period

# LOCATION / DEPARTMENT / PRODUCT / CATEGORY
def get_spend_by(spend_by, total_spend, total_spend_labels, total_spend_data, period_spend_data):
    # Set up for the arrays that are passed into charts.js
    for index, spend in enumerate(list(total_spend)):     
        total_spend_labels.append(spend[spend_by])
        total_spend_data.append(int(spend['total_spend']))

        # Add the Loc/Dept NAMES as the key for each element in loc/dept_period_spend_data dictionary
        # Using 'location/dept_spend' array because that contains data from ALL time periods, so should include ALL loc/dept_names
        period_spend_data[str(spend[spend_by])]=[0, 0, 0]
    return total_spend_labels, total_spend_data, period_spend_data


def get_period_spend_values(spend_by, items_by_period, period_spend_data):
    # Add the SPEND VALUES as an ARRAY for the relevant location (key) in location_period_spend_data dictionary
    # VALUES ARRAY: 1st (index=0) - spend in period_old, 2nd - period_mid, 3rd - period_today
    # Outer loop is to loop through items_by_period array
    # Inner loop is to loop through spend at each location in each items array (items_old etc)
    for i, period in enumerate(items_by_period):
        item_spend_by_period = list(period.values(spend_by).annotate(total_spend=Sum(F('qty_delivered')*F('price_ordered'), output_field=models.DecimalField())))
        for j, item in enumerate(item_spend_by_period):
            try:
                name = item[spend_by] 
                spend = int(item['total_spend']) 
                # Assign the spend to the (i-1)th element in the values array for that location
                period_spend_data[name][i] = spend
            except:
                pass
    return period_spend_data





