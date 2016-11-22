from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_verific_email(user,random_id):
    text_content = 'Hi {}, \n\n Please click on the following link to activate your account:\nhttp://127.0.0.1:8000/activate/?id=%s" %(id). \n\n If you have any questions, please reach out at support@eproc.com. \n\n Team at eProc'.format(user.first_name)
    html_content = '<h2>Hi {}, </h2> <div>Please click on the following link to activate your account:\nhttp://127.0.0.1:8000/activate/?id=%s" %(id)</div><br><div> If you have any questions, please reach out at support@eproc.com.</div><br><div> Team at eProc</div>'.format(user.first_name)
    msg = EmailMultiAlternatives("Activate your account", text_content, settings.DEFAULT_FROM_EMAIL, user.email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

