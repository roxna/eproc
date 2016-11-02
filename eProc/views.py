from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Max
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import modelformset_factory,BaseModelFormSet
from django.shortcuts import render, redirect, resolve_url
from django.template.response import TemplateResponse
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils import timezone
from django.utils.http import is_safe_url
from eProc.models import *
from eProc.forms import *



def home(request):
    return render(request, "home.html")

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='settings/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=LoginForm,
          current_app=None, extra_context=None):
    redirect_to = request.POST.get(redirect_field_name, '')
    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            auth_login(request, form.get_user())
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)
    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)

@login_required()
def dashboard(request):
	data = {

	}
	return render(request, "dashboard.html", data)

# to register & activate: https://github.com/JunyiJ/django-register-activate/blob/master/register_activate/views.py
@login_required
def users(request):
	# users = BuyerProfile.objects.filter(company=request.user.buyer_profile.company)
	users = BuyerProfile.objects.all()
	user_form = NewUserForm(request.POST or None)
	if request.method == "POST":
		if user_form.is_valid():
			user = user_form.save(commit=False)
			user.company = request.user.buyerCo
			user.save()
			text_content = 'Hey {}, \n\n Welcome to LezzGo! We are excited to have you be a part of our family. \n\n Let us know if we can answer any questions as you book or offer out your first ride. \n\n From the folks at LezzGo!'.format(user.first_name)
			html_content = '<h2>{}, Welcome to LezzGo!</h2> <div>We are excited to have you be a part of our family.</div><br><div>Let us know if we can answer any questions as you book or offer out your first ride.</div><br><div> Folks at LezzGo!</div>'.format(user.first_name)
			msg = EmailMultiAlternatives("Welcome to LezzGo!!", text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
			msg.attach_alternative(html_content, "text/html")
			# msg.send()
			return redirect('home')
	data = {
		'users': users,
		'user_form': user_form
	}
	return render(request, "settings/users.html", data)

@login_required
def departments(request):
	# departments = Department.objects.filter(company=request.user.buyer_profile.company)
	departments = Department.objects.all()
	department_form = DepartmentForm(request.POST or None)
	if request.method == "POST":
		if department_form.is_valid():
			department = department_form.save(commit=False)
			department.company = request.user.buyer_profile.company
			department.save()
			messages.success(request, "Department saved successfully")
			return redirect('/settings/departments')
	data = {
		'departments': departments,
		'department_form': department_form
	}
	return render(request, "settings/departments.html", data)

@login_required
def new_requisition(request):
    user = request.user
    OrderItemFormSet = modelformset_factory(model=OrderItem, form=OrderItemForm, formset=BaseModelFormSet, extra=1)
    requisition_form = RequisitionForm(request.POST or None)
    orderitem_formset = OrderItemFormSet(request.POST or None)
    if request.method == "POST":
        if requisition_form.is_valid() and orderitem_formset.is_valid():
            requisition = requisition_form.save(commit=False)
            requisition.preparer = user
            requisition.date_issued = datetime.now()
            requisition.buyerCo = user.buyer_profile.company            
            # Save the data for each form in the order_items formset
            for orderitem_form in orderitem_formset:
                order_item = orderitem_form.save(commit=False)
                if user.buyer_profile.role == 1 or user.buyer_profile.role == 3:
                	status = Status.objects.create(value=3, date=timezone.now, author=user, document=requisition)
            	else:
            		status = Status.objects.create(value=2, date=timezone.now, author=user, document=requisition)
            	status.save()
                order_item.requisition = requisition
                order_item.sub_total = order_item.product.unit_price * order_item.quantity
                requisition.sub_total += order_item.sub_total
                order_item.save()
            requisition.save()
            messages.success(request, 'Requisition submitted successfully')
            return redirect('/requisitions')
    data = {
	    'requisition_form': requisition_form,
	    'orderitem_formset': orderitem_formset
    }
    return render(request, "orders/new_requisition.html", data)


@login_required()
def requisitions(request):
    # requisitions = Requisition.objects.filter(buyerCo=request.user.buyer_profile.company).annotate(latest_update=Max('status_updates__date'))
    requisitions = Requisition.objects.get(pk=1)
    # requisitions = Requisition.objects.filter(buyerCo=request.user.buyer_profile.company).annotate(latest_update=Max('status_updates__date'))
    pending_requisitions = Requisition.objects.annotate(latest_update=Max('status_updates__date')).filter(status_updates=2)
    approved_requisitions = Requisition.objects.annotate(latest_update=Max('status_updates__date')).filter(status_updates=3)
    denied_requisitions = Requisition.objects.annotate(latest_update=Max('status_updates__date')).filter(status_updates=4)
    data = {
    	'requistions': requisitions,
    	'pending_requisitions': pending_requisitions,
    	'approved_requisitions': approved_requisitions,
    	'denied_requisitions': denied_requisitions,
    }
    return render(request, "orders/requisitions.html", data)

@login_required
def view_requisition(request, requisition_id):
    requisition = Requisition.objects.get(pk=requisition_id)
    data = {'requisition': requisition}
    return render(request, "orders/view_requisition.html", data)


