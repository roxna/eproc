from django.contrib import admin
from home.models import *

class AuthorAdmin(admin.ModelAdmin):
	list_display = ['name', 'source', 'title', 'company', 'email']

class BlogAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'date']
 
class PlanAdmin(admin.ModelAdmin):
	list_display = ['name', 'identifier', 'price', 'currency', 'interval', 'is_active', 'analytics', 'bulk_purchasing']

class TestimonialAdmin(admin.ModelAdmin):
	list_display = ['author', 'date']

class ContactRequestAdmin(admin.ModelAdmin):
	list_display = ['topic']

admin.site.register(Author, AuthorAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(ContactRequest, ContactRequestAdmin)