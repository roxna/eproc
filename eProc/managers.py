from django.db import models

class DocumentManager(models.Manager):
	def get_latest_status(self):	    
	    latest_status = None
	    for status in self.status_updates.all():
	        if latest_status is None or latest_status.date < status.date:
	            latest_status = status
	    return latest_status