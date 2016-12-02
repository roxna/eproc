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
    open_pos, closed_pos, cancelled_pos, paid_pos = [], [], [], []
    for po in pos:
        if po.get_latest_status().value == 'Open':            
            open_pos.append(po)
        elif po.get_latest_status().value == 'Closed':
            closed_pos.append(po)
        elif po.get_latest_status().value == 'Cancelled':
            cancelled_pos.append(po)
        elif po.get_latest_status().value == 'Paid':
            paid_pos.append(po)       
    all_pos = open_pos + closed_pos + cancelled_pos + paid_pos
    return all_pos, open_pos, closed_pos, cancelled_pos, paid_pos

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
            OrderItemStatus.objects.create(value='Approved', author=buyer, order_item=order_item)
    else:
        DocumentStatus.objects.create(value='Pending', author=buyer, document=requisition)
        for order_item in requisition.order_items.all():
            OrderItemStatus.objects.create(value='Requested', author=buyer, order_item=order_item)