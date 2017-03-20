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
		"upload": "fa-upload",
		"download": "fa-download",

		# Other
		"dashboard": "fa-dashboard",
		"alert": "fa-warning",
		"settings": "fa-gear",
		"analysis": "fa-area-chart",
		"industry": "fa-industry",
		"rating": "fa-star-o",

		# settings
		"locations": "fa-building",
		"company": "fa-institution",
		"profile": "fa-user",
		"users": "fa-users",
		"products": "fa-file-pdf-o",
		"products_bulk": "fa-money",
		"vendors": "fa-credit-card",
		"accounts": "fa-book",
		"taxes": "fa-percent",
		"approval": "fa-book",
		"charge": "fa-credit-card",

		# Notifications icons
		"Info": 'fa-flag text-blue',
		"Success": 'fa-check text-green',		
		"Warning": 'fa-warning text-yellow',
		"Error": 'fa-warning text-red',
	}
	return {'ICONS': icons}


# def buyer(request):
# 	return {'buyer': request.user.buyer_profile}

def notifications(request):
	# Get the count of unread_notifications and the 5 most recent ones for the user
	unread_notifications = Notification.objects.filter(recipients__id=request.user.pk, is_unread=True)
	notifications = {
		'count': unread_notifications.count(),
		'list': unread_notifications.order_by('-id')[:5],
	}
	return {'unread_notifications': notifications}

def price_alerts(request):
	# Get the count of price_alerts
	alerts = PriceAlert.objects.filter(is_active=True)
	try:		
		# In Admin panel, request.user doesn't have a buyer_profile
		 alerts = alerts.filter(buyer_co=request.user.buyer_profile.company)
	except:
		pass
	
	price_alerts = {
		'count': alerts.count(), #Total alerts set
		'user': request.user,
	}
	return {'price_alerts': price_alerts}	
	