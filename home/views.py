from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.views import generic
from django.utils import timezone
from django.utils.http import is_safe_url
from home.models import *
from home.forms import *

def home(request):
	plans = Plan.objects.filter(is_active=True)
	testimonials = Testimonial.objects.all().order_by('?')[:2]
	# Newsletter sign up
	if request.method == "POST":
		author, created = Author.objects.get_or_create(email=request.POST.get('email'))
		if created:
			author.name = request.POST.get('email')
			author.source = 'Newsletter'
			author.save()
		return redirect('success')
	data = {
		'plans': plans,
		'testimonials': testimonials,
	}
	return render(request, "home.html", data)

def pricing(request):
	plans = Plan.objects.filter(is_active=True)
	data = {
		'plans': plans,
	}
	return render(request, "pages/pricing.html", data)

def features(request):
    return render(request, "pages/features.html")

def contact(request):
	author_form = AuthorForm(request.POST or None)
	contact_form = ContactRequestForm(request.POST or None)	
	if request.method == "POST":
		if contact_form.is_valid() and author_form.is_valid():
			author, created = Author.objects.get_or_create(**author_form.cleaned_data)
			if created:
				author.source = 'Contact Form'
				author.save()
			contact_request = contact_form.save(commit=False)
			contact_request.author=author
			contact_request.save()
			return redirect('success')
		else:
			messages.error(request, 'Error. Request not sent.')
	data = {
		'contact_form': contact_form,
		'author_form': author_form
	}
	return render(request, "pages/contact.html", data)

def success(request):
	return render(request, "pages/success.html")

def blog(request):	
	blogs = Blog.objects.all().order_by('-date')[:5:1]
	data = {
		'blogs': blogs
	}
	return render(request, "pages/blog.html", data)

def faqs(request):
	return render(request, "pages/faqs.html")

def view_blog(request, blog_id, blog_slug):
    blog = Blog.objects.get(pk=blog_id)
    blog_id = int(blog_id)
    try:
    	prevBlog = Blog.objects.get(pk=blog_id-1)    	
    except:
    	prevBlog = Blog.objects.get(pk=blog_id)    	
    try:
    	nextBlog = Blog.objects.get(pk=blog_id+1)
    except:
    	nextBlog = Blog.objects.get(pk=blog_id)
    data = {
    	'blog': blog,
    	'prevBlog': prevBlog,
    	'nextBlog': nextBlog,
    }
    return render(request, "pages/blogpost.html", data)

def terms(request):
	return render(request, "legal/terms.html")

def privacy_policy(request):
	return render(request, "legal/privacy_policy.html")