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

class ContactRequest(models.Model):
	TOPICS = (
		('Demo', 'I want to book a demo'),
		('Pricing', 'I have a question about pricing'),
		('Billing', 'I have a question about billing'),
		('Partnerships', 'I want to talk about partnerships'),
		('Other', 'Other'),
	)
	topic = models.CharField(choices=TOPICS, max_length=15)
	name = models.CharField(max_length=50)
	company = models.CharField(max_length=50)
	email = models.EmailField(max_length=254)
	date = models.DateTimeField(default=timezone.now)
	body = models.TextField(null=True, blank=True)

	def __unicode__(self):
		return "{}({}) about {}".format(self.name, self.email, self.topic)
