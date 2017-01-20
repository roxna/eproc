from django.db import models
from django.db.models import Max

# Manager to get the latest status of each DOCUMENT or ORDER ITEM (manager shared between both models)
class LatestStatusManager(models.Manager):

	def _get_pending(self):
		pending_list = ['Pending']
		return super(LatestStatusManager, self).get_queryset().annotate(latest_update=Max('status_updates__date')).filter(status_updates__value__in=pending_list)

	def _get_approved(self):
		approved_list = ['Approved']
		return super(LatestStatusManager, self).get_queryset().annotate(latest_update=Max('status_updates__date')).filter(status_updates__value__in=approved_list)

	def _get_delivered(self):
		delivered_list = ['Delivered Partial', 'Delivered Complete']
		return super(LatestStatusManager, self).get_queryset().annotate(latest_update=Max('status_updates__date')).filter(status_updates__value__in=delivered_list)	

	pending = property(_get_pending)
	approved = property(_get_approved)
	delivered = property(_get_delivered)