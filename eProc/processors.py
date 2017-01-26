from eProc.models import *

from django.template import Context


# Custom Django context processor methods allow you to set up data for access on all Django project templates.

def icons(request):
	icons = {
		# docs
		"requisition": "fa-shopping-cart",
		"po": "fa-shopping-cart",
		"invoice": "fa-shopping-cart",
		"receive": "fa-truck",
		"drawdown": "fa-sign-out",
		"settings": "fa-gear",
		"analysis": "fa-area-chart",

		# settings
		"locations": "fa-building",
		"company": "fa-institution",
		"profile": "fa-user",
		"users": "fa-users",
		"products": "fa-file-pdf-o",
		"vendors": "fa-credit-card",
		"accounts": "fa-book",
		"approval": "fa-book",
	}
	return {'ICONS': icons}


