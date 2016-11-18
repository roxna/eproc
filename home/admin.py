from django.contrib import admin
from home.models import *

class BlogAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'date']
 
class PlanAdmin(admin.ModelAdmin):
	list_display = ['name', 'price_per_user']

admin.site.register(Blog, BlogAdmin)
admin.site.register(Plan, PlanAdmin)