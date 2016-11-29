from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from django.contrib.auth.views import login, logout
from django.contrib.auth import views as auth_views
from home import views as home_views
from eProc import views as eProc_views
from eProc.forms import LoginForm

urlpatterns=[
#     # Examples:
#     # url(r'^$', 'eProcure.views.home', name='home'),
#     # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),


    #####################################
    ## HOME - LANDING PAGE, BLOGS ETC  ##
    #####################################
    # GENERAL
    url(r'^$', home_views.home, name='home'),
    url(r'^pricing/$', home_views.pricing, name='pricing'),
    url(r'^features/$', home_views.features, name='features'),
    url(r'^blog/$', home_views.blog, name='blog'),
    url(r'^blog/(?P<blog_id>\w+)/(?P<blog_slug>[\w-]+)/$', home_views.view_blog, name='view_blog'), 
    url(r'^contact/$', home_views.contact, name='contact'),
    url(r'^success/$', home_views.success, name='success'),
    
    # LEGAL
    url(r'^terms/$', home_views.terms, name='terms'),
    url(r'^privacy-policy/$', home_views.privacy_policy, name='privacy_policy'),

    ###### REGISTRATION URLS (in eProc) ######
    url(r'^register/$', eProc_views.register, name='register'),
    url(r'^activate/$', eProc_views.activate, name='activate'),
    url(r'^login/$', login, {'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^thankyou/$', eProc_views.thankyou, name='thankyou'),
    
    # Reset Password - https://docs.djangoproject.com/en/1.8/_modules/django/contrib/auth/views/
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    # TODO: password_change isn't passing messages framework as extra_context to show pw changed success
    url(r'^password_change/$', auth_views.password_change, {'post_change_redirect': 'user_profile', 'extra_context': { 'messages': 'Password changed successfully'}}, name='password_change'),
    # url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),


    #####################################
    ##         EPROCURE MODULE         ##
    #####################################
    # Post log in URLS
    url(r'^get-started/$', eProc_views.get_started, name='get_started'),
    url(r'^dashboard/$', eProc_views.dashboard, name='dashboard'),
    url(r'^requisition/new/$', eProc_views.new_requisition, name='new_requisition'),
    url(r'^requisitions/$', eProc_views.requisitions, name='requisitions'),
    url(r'^requisitions/(?P<requisition_id>\w+)/$', eProc_views.view_requisition, name='view_requisition'),
    
    url(r'^purchase-orders/$', eProc_views.purchaseorders, name='purchaseorders'),
    url(r'^purchase-order/new/$', eProc_views.new_purchaseorder, name='new_purchaseorder'),
    url(r'^purchase-order/(?P<po_id>\w+)/$', eProc_views.view_purchaseorder, name='view_purchaseorder'),
    url(r'^purchase-order/print/(?P<po_id>\w+)$', eProc_views.print_purchaseorder, name='print_purchaseorder'),
    url(r'^purchase-orders/receive/$', eProc_views.receive_pos, name='receive_pos'),
    url(r'^purchase-order/receive/(?P<po_id>\w+)/$', eProc_views.receive_purchaseorder, name='receive_purchaseorder'),

    url(r'^invoices/$', eProc_views.invoices, name='invoices'),
    url(r'^invoice/new/$', eProc_views.new_invoice, name='new_invoice'),
    # url(r'^invoice/(?P<invoice_id>\w+)/$', eProc_views.view_invoice, name='view_invoice'),
    url(r'^inventory/$', eProc_views.inventory, name='inventory'),
    
    url(r'^vendors/$', eProc_views.vendors, name='vendors'),
    url(r'^vendor/(?P<vendor_id>\w+)/(?P<vendor_name>[\w-]+)/$', eProc_views.view_vendor, name='view_vendor'),
    url(r'^vendors/import-csv$', eProc_views.upload_vendor_csv, name='upload_vendor_csv'),
    url(r'^products/$', eProc_views.products, name='products'),
    url(r'^products/import-csv$', eProc_views.upload_product_csv, name='upload_product_csv'),
    url(r'^categories/$', eProc_views.categories, name='categories'),

    url(r'^settings/profile/$', eProc_views.user_profile, name='user_profile'),
    url(r'^settings/company/$', eProc_views.company_profile, name='company_profile'),
    url(r'^settings/users/$', eProc_views.users, name='users'),
    url(r'^settings/departments/$', eProc_views.departments, name='departments'),
    url(r'^settings/account-codes/$', eProc_views.account_codes, name='account_codes'),
    # url(r'^settings/taxes/$', eProc_views.taxes, name='taxes'),


]


