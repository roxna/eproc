from django.db import models
from django.db.models import Sum, Max, Avg, F, Q

# class FeatureManager(models.Manager):

#     @staticmethod
#     def _test_cases_eq_0( qs ):
#        return qs.annotate( num_test_cases=models.Count('testcase_set') ).filter(num_test_cases=0)

#     @staticmethod
#     def _standardized_gt_0( qs ):
#         return qs.annotate( standardised=Count('documentation_set__standard') ).filter(standardised__gt=0)

#     def without_test_cases(self):
#         return self._test_cases_eq_0( self.get_query_set() )

#     def standardised(self):
#         return self._standardized_gt_0( self.get_query_set() )

#     def intersection( self ):
#         return self._test_cases_eq_0( self._standardized_gt_0( self.get_query_set() ) )


# Manager to get the latest status of each Document or Order Item
class LatestStatusManager(models.Manager):
	use_for_related_fields = True

	def _get_pending(self):
		pending_list = ['Pending']
		return super(LatestStatusManager, self).get_queryset().annotate(latest_update=Max('status_updates__date')).filter(status_updates__value__in=pending_list)

	def _get_approved(self):
		approved_list = ['Approved']
		return super(LatestStatusManager, self).get_queryset().annotate(latest_update=Max('status_updates__date')).filter(status_updates__value__in=approved_list)

	def _get_delivered(self):
		delivered_list = ['Delivered Partial', 'Delivered Complete']
		return self.get_queryset().annotate(latest_update=Max('status_updates__date')).filter(status_updates__value__in=delivered_list)	

	pending = property(_get_pending)
	approved = property(_get_approved)
	delivered = property(_get_delivered)