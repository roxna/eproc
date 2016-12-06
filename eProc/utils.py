from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Max
from django.utils import timezone
from eProc.models import *

def send_verific_email(user,random_id):
    text_content = 'Hi {}, \n\n Please click on the following link to activate your account:\nhttp://127.0.0.1:8000/activate/?id={}". \n\n If you have any questions, please reach out at support@eproc.com. \n\n Team at eProc'.format(user.first_name, random_id)
    html_content = '<div>Hi {},</div><br><div>Please click on the following link to activate your account: http://127.0.0.1:8000/activate/?id={}" </div><br><div> If you have any questions, please reach out at support@eproc.com.</div><br><div> Team at eProc</div>'.format(user.first_name, random_id)
    msg = EmailMultiAlternatives("Activate your account", text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# TODO CLEANER IMPLEMENTATION OF QUERIES
def get_requisitions(requisitions):    
    pending_requisitions, approved_requisitions, denied_requisitions = [], [], []
    for requisition in requisitions:
        if requisition.get_latest_status().value == 'Pending':            
            pending_requisitions.append(requisition)
        elif requisition.get_latest_status().value == 'Approved':
            approved_requisitions.append(requisition)
        elif requisition.get_latest_status().value == 'Denied':
            denied_requisitions.append(requisition)   
    all_requisitions = pending_requisitions + approved_requisitions + denied_requisitions
    
    # latest_statuses = DocumentStatus.objects.filter(latest_update)    
    # pending_status_list = DocumentStatus.objects.filter(latest_update)
    # pending_requisitions = requisitions.filter(status_updates__in=pending_status_list)
    # DocumentStatus.objects.annotate(latest_update=Max('date')).filter()
    # all_requisitions = requisitions.annotate(latest_update=Max('status_updates__date'))
    # pending_requisitions = all_requisitions.filter(status_updates__value='Pending')    
    return all_requisitions, pending_requisitions, approved_requisitions, denied_requisitions

# TODO: See Get_requisitions
def get_pos(pos):
    pending_pos, open_pos, closed_pos, paid_pos, cancelled_pos, denied_pos  = [], [], [], [], [], []
    for po in pos:
        if po.get_latest_status().value == 'Pending':
            pending_pos.append(po)
        if po.get_latest_status().value == 'Open':            
            open_pos.append(po)
        elif po.get_latest_status().value == 'Closed':
            closed_pos.append(po)
        elif po.get_latest_status().value == 'Paid':
            paid_pos.append(po)           
        elif po.get_latest_status().value == 'Cancelled':
            cancelled_pos.append(po)
        elif po.get_latest_status().value == 'Denied':
            denied_pos.append(po)                   
    all_pos = pending_pos + open_pos + closed_pos + cancelled_pos + paid_pos + denied_pos
    return all_pos, pending_pos, open_pos, closed_pos, paid_pos, cancelled_pos, denied_pos

# TODO: See Get_requisitions
def get_invoices(invoices):
    all_invoices, pending_invoices, approved_invoices, cancelled_invoices, paid_invoices = [], [], [], [], []
    for invoice in invoices:
        if invoice.get_latest_status().value == 'Pending':
            pending_invoices.append(invoice)
        elif invoice.get_latest_status().value == 'Approved':
            approved_invoices.append(invoice)
        elif invoice.get_latest_status().value == 'Cancelled':
            cancelled_invoices.append(invoice)
        elif invoice.get_latest_status().value == 'Paid':
            paid_invoices.append(invoice)       
    all_invoices = pending_invoices + approved_invoices + cancelled_invoices + paid_invoices
    return all_invoices, pending_invoices, approved_invoices, cancelled_invoices, paid_invoices

################################
###     NEW REQUISITION     ### 
################################ 

def initialize_newreq_forms(user, requisition_form, orderitem_formset):
    requisition_form.fields['department'].queryset = Department.objects.filter(company=user.buyer_profile.company)
    requisition_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=user.buyer_profile.company).exclude(user=user)
    for orderitem_form in orderitem_formset: 
        orderitem_form.fields['product'].queryset = CatalogItem.objects.filter(buyer_co=user.buyer_profile.company)
        orderitem_form.fields['account_code'].queryset = AccountCode.objects.filter(company=user.buyer_profile.company)

def save_new_requisition(buyer, requisition_form):
    requisition = requisition_form.save(commit=False)
    requisition.preparer = buyer
    requisition.currency = buyer.company.currency
    requisition.date_issued = timezone.now()
    requisition.buyer_co = buyer.company
    requisition.sub_total = 0
    requisition.save()
    return requisition

def save_newreq_orderitems(requisition, orderitem_formset):
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
            order_item.unit_price = order_item.product.unit_price
            order_item.save()
    requisition.save()

def save_newreq_statuses(buyer, requisition):
    if buyer.role == 'SuperUser':
        DocumentStatus.objects.create(value='Approved', author=buyer, document=requisition)
        for order_item in requisition.order_items.all():
            OrderItemStatus.objects.create(value='Requested', author=buyer, order_item=order_item)
    else:
        DocumentStatus.objects.create(value='Pending', author=buyer, document=requisition)
        for order_item in requisition.order_items.all():
            OrderItemStatus.objects.create(value='Open', author=buyer, order_item=order_item)


################################
###    NEW PURCHASE ORDER    ### 
################################ 





################################
###        UPLOAD CSVs       ### 
################################ 

def handle_product_upload(reader, buyer_co):
    for row in reader:
        name = row['PRODUCT_NAME']
        desc = row['DESCRIPTION']
        sku = row['SKU']
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


