from __future__ import unicode_literals
from django.utils import timezone
from django.db import models


class Author(models.Model):
	name = models.CharField(max_length=40, null=True, blank=True)
	SOURCES = (('Blog Author', 'Blog Author'), ('Contact Form', 'Contact Form'), ('Newsletter', 'Newsletter'))
	source = models.CharField(choices=SOURCES, max_length=40)
	title = models.CharField(max_length=40, null=True, blank=True)
	company = models.CharField(max_length=50, null=True, blank=True)
	email = models.EmailField(max_length=254, null=True, blank=True)	

	def __unicode__(self):
		return "{}".format(self.name)

class Blog(models.Model):
	title = models.CharField(max_length=100)
	summary = models.TextField()
	content = models.TextField()	
	date = models.DateField(default=timezone.now)
	image = models.ImageField(blank=True, null=True)  # No upload_to here because it would go into MEDIA_ROOT instead of being served from static_files
	author = models.ForeignKey(Author, related_name="blogs")

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
	author = models.ForeignKey(Author, related_name="contact_requests")		
	date = models.DateTimeField(default=timezone.now)
	body = models.TextField(null=True, blank=True)

	def __unicode__(self):
		return "{}({})".format(self.topic, self.author.name)

class Testimonial(models.Model):
	body = models.TextField()
	author = models.ForeignKey(Author, related_name="testimonials")
	date = models.DateTimeField(default=timezone.now)

