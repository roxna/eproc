from django.db import models
from django.db.models import F, Max
from django.conf import settings

# Manager to get the latest status of each DOCUMENT or ORDER ITEM (manager shared between both models)
class LatestStatusManager(models.Manager):

	def _get_latest_status(self, status_list):
		return super(LatestStatusManager, self).get_queryset().annotate(latest_update=Max('status_updates__date')).filter(status_updates__date=F('latest_update'), status_updates__value__in=status_list)

	
	'''
	Statuses that likely have MULTIPL entries with the values 
	Eg. Multiple deliveries --> multiple 'Delivered' status updates
	'''
	def _get_pending(self):
		return self._get_latest_status(['Pending'])

	def _get_approved(self):
		return self._get_latest_status(['Approved'])

	def _get_delivered(self):
		return self._get_latest_status(['Delivered'])

	def _get_ordered(self):
		return self._get_latest_status(['Ordered'])

	
	'''
	Statuses that likely have SINGLES entries with the values 
	Eg. Once PO is closed, it is Closed
	Will have to change this if we want POs to be opened again etc
	In that case, replicate 'current_status' for Docs (like Items)
	'''
	
	def _get_open(self):
		return self._get_latest_status(['Open'])

	def _get_denied(self):
		return self._get_latest_status(['Denied'])

	def _get_cancelled(self):
		return self._get_latest_status(['Cancelled'])		

	def _get_closed(self):
		return self._get_latest_status(['Closed'])		


	# Set them as properties so can call OrderItem.latest_status_objects.delivered etc
	pending = property(_get_pending)
	opened = property(_get_open)
	approved = property(_get_approved)
	delivered = property(_get_delivered)

	denied = property(_get_denied)
	ordered = property(_get_ordered)
	cancelled = property(_get_cancelled)
	closed = property(_get_closed)


