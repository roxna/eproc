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

# TODO CLEANER IMPLEMENTATION OF QUERIES
def get_documents(documents): 
    pending_docs, approved_docs, closed_docs, paid_docs, cancelled_docs, denied_docs = [], [], [], [], [], []
    
    # (doc.get_latest_status().value.lower + '_requisitions').append(doc) for doc in documents
    for doc in documents:
        if doc.get_latest_status().value == 'Pending':            
            pending_docs.append(doc)
        elif doc.get_latest_status().value == 'Approved':
            approved_docs.append(doc)
        elif doc.get_latest_status().value == 'Closed':
            closed_docs.append(doc)
        elif doc.get_latest_status().value == 'Paid':
            paid_docs.append(doc)                
        elif doc.get_latest_status().value == 'Cancelled':
            cancelled_docs.append(doc)        
        elif doc.get_latest_status().value == 'Denied':
            denied_docs.append(doc)  
                       
    all_docs = pending_docs + approved_docs + closed_docs + paid_docs + cancelled_docs + denied_docs
    return all_docs, pending_docs, approved_docs, closed_docs, paid_docs, cancelled_docs, denied_docs


################################
###     COMMON METHODS     ### 
################################ 

# Used by NEW_REQ, NEW_PO, NEW_INVOICE, NEW_DD
def save_new_document(buyer, form):
    instance = form.save(commit=False)
    instance.preparer = buyer
    instance.currency = buyer.company.currency
    instance.date_issued = timezone.now()
    instance.buyer_co = buyer.company
    instance.sub_total = 0
    instance.save()
    return instance

# Save the data for each form in the order_items formset 
# Used by NEW_REQ, NEW_DD
def save_orderitems(document, orderitem_formset):    
    for index, orderitem_form in enumerate(orderitem_formset.forms):
        if orderitem_form.is_valid():
            order_item = orderitem_form.save(commit=False)
            order_item.number = document.number + "-" + str(index+1)
            if isinstance(document, Requisition):
                order_item.requisition = document
            elif isinstance(document, Drawdown):
                order_item.drawdown = document
            order_item.date_due = document.date_due                    
            order_item.sub_total = orderitem_form.cleaned_data['product'].unit_price * orderitem_form.cleaned_data['quantity']
            document.sub_total += order_item.sub_total            
            order_item.save()                    
            order_item.unit_price = order_item.product.unit_price
            order_item.save()
    document.save()


################################
###     NEW REQUISITION     ### 
################################ 

def initialize_newreq_forms(user, requisition_form, orderitem_formset):
    requisition_form.fields['department'].queryset = Department.objects.filter(company=user.buyer_profile.company)
    requisition_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=user.buyer_profile.company).exclude(user=user)
    for orderitem_form in orderitem_formset: 
        orderitem_form.fields['product'].queryset = CatalogItem.objects.filter(buyer_co=user.buyer_profile.company)
        orderitem_form.fields['account_code'].queryset = AccountCode.objects.filter(company=user.buyer_profile.company)

def save_newreq_statuses(buyer, requisition):
    if buyer.role == 'SuperUser':
        DocumentStatus.objects.create(value='Approved', author=buyer, document=requisition)
        for order_item in requisition.order_items.all():
            OrderItemStatus.objects.create(value='Approved', author=buyer, order_item=order_item)
    else:
        DocumentStatus.objects.create(value='Pending', author=buyer, document=requisition)
        for order_item in requisition.order_items.all():
            OrderItemStatus.objects.create(value='Requested', author=buyer, order_item=order_item)

################################
###    NEW PURCHASE ORDER    ### 
################################ 

def initialize_newpo_forms(buyer, po_form):
    po_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=buyer.company)
    po_form.fields['billing_add'].queryset = Location.objects.filter(company=buyer.company)
    po_form.fields['shipping_add'].queryset = Location.objects.filter(company=buyer.company)
    po_form.fields['vendor_co'].queryset = VendorCo.objects.filter(buyer_co=buyer.company)


################################
###       DRAWDOWNS         ### 
################################ 

def initialize_newdrawdown_forms(user, drawdown_form, drawdownitem_formset):
    drawdown_form.fields['department'].queryset = Department.objects.filter(company=user.buyer_profile.company)
    drawdown_form.fields['next_approver'].queryset = BuyerProfile.objects.filter(company=user.buyer_profile.company).exclude(user=user)
    for drawdownitem_form in drawdownitem_formset: 
        drawdownitem_form.fields['product'].queryset = CatalogItem.objects.filter(buyer_co=user.buyer_profile.company)

def save_newdrawdown_statuses(buyer, drawdown):
    if buyer.role == 'SuperUser':
        DocumentStatus.objects.create(value='Approved', author=buyer, document=drawdown)
        for order_item in drawdown.order_items.all():
            OrderItemStatus.objects.create(value='Drawdown Approved', author=buyer, order_item=order_item)
    else:
        DocumentStatus.objects.create(value='Pending', author=buyer, document=drawdown)
        for order_item in drawdown.order_items.all():
            OrderItemStatus.objects.create(value='Drawdown Requested', author=buyer, order_item=order_item)

def get_inventory_received(all_items):
    available_for_drawdown_statuses = ['Delivered Partial', 'Delivered Complete']
    delivered_ids = [item.id for item in all_items if item.get_latest_status().value in available_for_drawdown_statuses]
    delivered_list = all_items.filter(id__in=delivered_ids)
    delivered_count = delivered_list.values('product__name').annotate(total_qty=Sum('quantity'))
    return delivered_list, delivered_count

def get_inventory_drawndown(all_items, multiplier=1):    
    drawndown_statuses = ['Drawdown Approved']
    drawndown_ids = [item.id for item in all_items if item.get_latest_status().value in drawndown_statuses]
    drawndown_list = all_items.filter(id__in=drawndown_ids)
    drawndown_count = drawndown_list.values('product__name').annotate(total_qty=Sum('quantity')*multiplier)    
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





