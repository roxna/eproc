from home.models import *
from django.template import Context
from django.conf import settings as conf_settings

def contact(request):
	contact = {
		'email': conf_settings.CONTACT_EMAIL,
		'phone': conf_settings.CONTACT_PHONE,
	}
	return {'contact': contact}
