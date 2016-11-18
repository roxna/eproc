from __future__ import unicode_literals
from django.utils import timezone
from django.db import models

class Blog(models.Model):
	title = models.CharField(max_length=40)
	summary = models.TextField()
	content = models.TextField()
	author = models.CharField(max_length=40)
	date = models.DateField(default=timezone.now)
	image = models.ImageField(upload_to='blogs', blank=True, null=True)

	def __unicode__(self):
		return "{}".format(self.title)

class Plan(models.Model):
	name = models.CharField(max_length=20)
	price_per_user = models.IntegerField(default=10)

	def __unicode__(self):
		return "{} - ${}/user".format(self.name, self.price_per_user)
