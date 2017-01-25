from django.db import models
from django.db.models import Max

# Manager to get the latest status of each DOCUMENT or ORDER ITEM (manager shared between both models)
class LatestStatusManager(models.Manager):

	def _get_by_status(self, status_list):
		return super(LatestStatusManager, self).get_queryset().annotate(latest_update=Max('status_updates__date')).filter(status_updates__value__in=status_list)

	def _get_pending(self):
		return self._get_by_status(['Pending'])
	
	def _get_open(self):
		return self._get_by_status(['Open'])

	def _get_approved(self):
		return self._get_by_status(['Approved'])

	def _get_delivered(self):
		return self._get_by_status(['Delivered Partial', 'Delivered Complete'])

	def _get_denied(self):
		return self._get_by_status(['Denied'])
	
	def _get_ordered(self):
		return self._get_by_status(['Ordered'])

	def _get_cancelled(self):
		return self._get_by_status(['Cancelled'])

	def _get_paid(self):
		return self._get_by_status(['Paid'])		

	def _get_closed(self):
		return self._get_by_status(['Closed'])

	def _get_archived(self):
		return self._get_by_status(['Archived'])	

	def _get_delivered_partial(self):
		return self._get_by_status(['Delivered Partial'])

	def _get_delivered_complete(self):
		return self._get_by_status(['Delivered Complete'])		

	def _get_drawdown_requested(self):
		return self._get_by_status(['Drawdown Requested'])

	def _get_drawdown_approved(self):
		return self._get_by_status(['Drawdown Approved'])	

	def _get_drawdown_denied(self):
		return self._get_by_status(['Drawdown Denied'])

	def _get_drawdown_cancelled(self):
		return self._get_by_status(['Drawdown Cancelled'])	

	# Set them as properties so can call OrderItem.latest_status_objects.delivered etc
	pending = property(_get_pending)
	opened = property(_get_open)
	approved = property(_get_approved)
	delivered = property(_get_delivered)
	delivered_partial = property(_get_delivered_partial)
	delivered_complete = property(_get_delivered_complete)

	denied = property(_get_denied)
	ordered = property(_get_ordered)
	cancelled = property(_get_cancelled)
	paid = property(_get_paid)	
	closed = property(_get_closed)
	archived = property(_get_archived)

	drawdown_requested = property(_get_drawdown_requested)
	drawdown_approved = property(_get_drawdown_approved)
	drawdown_denied = property(_get_drawdown_denied)
	drawdown_cancelled = property(_get_drawdown_cancelled)

