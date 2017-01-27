from eProc.models import *
from django.template import Context


# Custom Django context processor methods 
# Allow you to set up data for access on all templates
def icons(request):
	icons = {
		# docs
		"requisition": "fa-book",
		"po": "fa-shopping-cart",
		"invoice": "fa-shopping-cart",
		"receive": "fa-truck",
		"drawdown": "fa-sign-out",
		"payment": "fa-money",
		"inventory": "fa-list-alt",
		
		"new": "fa-pencil-square-o",
		"incoming": "fa-arrow-down",
		"outgoing": "fa-arrow-up",

		# Other
		"dashboard": "fa-dashboard",
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


def buyer(request):
	return {'buyer': request.user.buyer_profile}
