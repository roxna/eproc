from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Max

def send_verific_email(user,random_id):
    text_content = 'Hi {}, \n\n Please click on the following link to activate your account:\nhttp://127.0.0.1:8000/activate/?id={}". \n\n If you have any questions, please reach out at support@eproc.com. \n\n Team at eProc'.format(user.first_name, random_id)
    html_content = '<div>Hi {},</div><br><div>Please click on the following link to activate your account: http://127.0.0.1:8000/activate/?id={}" </div><br><div> If you have any questions, please reach out at support@eproc.com.</div><br><div> Team at eProc</div>'.format(user.first_name, random_id)
    msg = EmailMultiAlternatives("Activate your account", text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def get_pos(all_pos):
    open_pos = all_pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Open')
    closed_pos = all_pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Closed')
    cancelled_pos = all_pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Cancelled')
    paid_pos = all_pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Paid')
    return open_pos, closed_pos, cancelled_pos, paid_pos