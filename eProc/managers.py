from django.db import models

# class DocumentQueryset(models.QuerySet):
# 	def get_latest_status(self):	    
# 	    latest_status = None
# 	    for status in self.status_updates.all():
# 	        if latest_status is None or latest_status.date < status.date:
# 	            latest_status = status
# 	    return latest_status

# class DocumentManager(models.Manager):
# 	def get_query_set(self):
# 		return DocumentQueryset(self.model)

# 	def get_latest_status(self):
# 		return self.get_query_set().get_latest_status()
	
# Manager to get the latest status of each Document or Order Item
class LatestStatusManager(models.Manager):
	def get_query_set(self):
		return super(LatestStatusManager, self).get_queryset().annotate(Max('status_updates__date'))

class OrderItemManager(models.Manager):

	def get_item_ids_with_status(items_to_query, status_list):
		return [item.id for item in items_to_query if item.get_latest_status().value in status_list]

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