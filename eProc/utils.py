from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Max, Sum
from django.utils import timezone
from eProc.models import *

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


################################
###    INITIALIZE FORMS    ### 
################################ 

def initialize_req_form(buyer, requisition_form, orderitem_formset):
    if buyer.role == 'SuperUser':
        # If SuperUser, can select any department and approver, incl. self
        requisition_form.fields['department'].queryset = Department.objects.filter(location__in=buyer.company.get_all_locations())
        requisition_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company, role__in=['Approver', 'SuperUser'])
    else:
        # Else, dept only of buyer's location and next_approver only in buyer's department
        requisition_form.fields['department'].queryset = Department.objects.filter(location=buyer.location)
        requisition_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(department=buyer.department, role__in=['Approver', 'SuperUser']).exclude(user=buyer.user)
    
    for form in orderitem_formset: 
        form.fields['product'].queryset = CatalogItem.objects.filter(buyer_co=buyer.company)
        form.fields['account_code'].queryset = AccountCode.objects.filter(company=buyer.company)

def initialize_po_form(buyer, po_form):
    po_form.fields['billing_add'].queryset = Location.objects.filter(company=buyer.company)
    po_form.fields['shipping_add'].queryset = Location.objects.filter(company=buyer.company)
    po_form.fields['vendor_co'].queryset = VendorCo.objects.filter(buyer_co=buyer.company) 

def initialize_invoice_form(buyer, invoice_form):
    invoice_form.fields['vendor_co'].queryset = VendorCo.objects.filter(buyer_co=buyer.company)
    # TODO: POs with UNBILLED ITEMS ONLY 
    invoice_form.fields['purchase_order'].queryset = PurchaseOrder.objects.filter(buyer_co=buyer.company)
    invoice_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company, role__in=['Payer', 'SuperUser'])

def initialize_drawdown_form(buyer, drawdown_form, drawdownitem_formset):
    drawdown_form.fields['department'].queryset = Department.objects.filter(location=buyer.location)
    drawdown_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company).exclude(user=buyer.user)
    for drawdownitem_form in drawdownitem_formset: 
        drawdownitem_form.fields['product'].queryset = CatalogItem.objects.filter(buyer_co=buyer.company)
    drawdown_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company, role__in=['Inventory Manager', 'Branch Manager', 'SuperUser'])


################################
###   SAVE METHODS - COMMON  ### 
################################ 

# Used by NEW_REQ, NEW_PO, NEW_INVOICE, NEW_DD

def set_next_approver_not_required(buyer, form):
    if buyer.role == 'SuperUser':
        form.fields['next_approver'].required = False

def save_new_document(buyer, form):
    instance = form.save(commit=False)
    instance.preparer = buyer
    instance.currency = buyer.company.currency
    instance.date_issued = timezone.now()
    instance.buyer_co = buyer.company
    instance.save()
    return instance

# Save the data for each form in the order_items formset 
# Used by NEW_REQ, NEW_DD
def save_items(buyer, document, orderitem_formset):    
    for index, form in enumerate(orderitem_formset.forms):
        if form.is_valid():
            item = form.save(commit=False)
            item.date_due = document.date_due
            if isinstance(document, Requisition):
                item.number = document.number + "-" + str(index+1)
                item.requisition = document
                document.sub_total += item.get_requested_subtotal()
                if buyer.role == 'SuperUser':
                    item.qty_approved = item.qty_requested
                item.unit_price = item.product.unit_price
            elif isinstance(document, PurchaseOrder):
                item.purchase_order = document
                if buyer.role == 'SuperUser':
                    item.qty_ordered = item.qty_approved            
            elif isinstance(document, Drawdown):
                item.unit_price = item.product.unit_price  #Don't like this being set here
                item.drawdown = document
            item.save()
    document.save()

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

# Updates document and order_item statuses with relevant values/author
def save_status(document, doc_status, item_status, author):
    save_doc_status(document, doc_status, author)
    save_item_status(document, item_status, author)

def save_doc_status(document, doc_status, author):
    DocumentStatus.objects.create(document=document, value=doc_status, author=author)

def save_item_status(document, item_status, author):
    for item in document.items.all():
        if isinstance(document, Drawdown):
            DrawdownItemStatus.objects.create(value=item_status, author=author, item=item)
        else:
            OrderItemStatus.objects.create(value=item_status, author=author, item=item)

################################
###        GET METHODS       ### 
################################ 

def get_inventory_received(all_items):
    available_for_drawdown_statuses = ['Delivered Partial', 'Delivered Complete']
    delivered_ids = [item.id for item in all_items if item.get_latest_status().value in available_for_drawdown_statuses]
    delivered_list = all_items.filter(id__in=delivered_ids)
    delivered_count = delivered_list.values('product__name', 'product__threshold').annotate(total_qty=Sum('qty_delivered'))
    return delivered_list, delivered_count

def get_inventory_drawndown(all_items, multiplier=1):    
    drawndown_statuses = ['Drawdown Approved']
    drawndown_ids = [item.id for item in all_items if item.get_latest_status().value in drawndown_statuses]
    drawndown_list = all_items.filter(id__in=drawndown_ids)
    drawndown_count = drawndown_list.values('product__name', 'product__threshold').annotate(total_qty=Sum('qty_drawndown')*multiplier)    
    return drawndown_list, drawndown_count


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
        vendor_co, vendor_created = VendorCo.objects.get_or_create(name=row['VENDOR'], buyer_co=buyer_co, currency=buyer_co.currency)
        CatalogItem.objects.get_or_create(name=name, desc=desc, sku=sku, unit_price=unit_price, unit_type=unit_type, currency=vendor_co.currency, category=category, vendor_co=vendor_co, buyer_co=buyer_co)

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
                                                                   contact_rep=contact_rep, comments=comments, buyer_co=buyer_co)        
        location = Location.objects.get_or_create(address1=address1, address2=address2, city=city, state=state, zipcode=zipcode, 
                                                  country=country, phone=phone, email=email, company=vendor_co)







