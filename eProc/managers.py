from django.db import models

class DocumentQueryset(models.query.QuerySet):
	def get_latest_status(self):	    
	    latest_status = None
	    for status in self.status_updates.all():
	        if latest_status is None or latest_status.date < status.date:
	            latest_status = status
	    return latest_status

class DocumentManager(models.Manager):
	def get_query_set(self):
		return DocumentQueryset(self.model)

	def get_latest_status(self):
		return self.get_query_set().get_latest_status()
	