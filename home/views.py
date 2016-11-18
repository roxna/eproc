from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views import generic
from django.utils import timezone
from django.utils.http import is_safe_url
from home.models import *

def home(request):
    return render(request, "home.html")

def pricing(request):
    return render(request, "pages/pricing.html")

def features(request):
    return render(request, "pages/features.html")

def contact(request):
    return render(request, "pages/contact.html")

def blog(request):
	blogs = Blog.objects.all().order_by('-date')[:5:1]
	data = {
		'blogs': blogs
	}
	return render(request, "pages/blog.html", data)

def view_blog(request, blog_id):
    blog_id = Blog.objects.get(pk=blog_id)
    data = {
    	'blog': blog,
    	'prevPost': blog,
    	'nextPost': blog,
    }
    return render(request, "pages/blogpost.html", data)