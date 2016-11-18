from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from django.contrib.auth.views import logout
from home import views as home_views
from eProc import views as eProc_views

urlpatterns=[
    # Examples:
    # url(r'^$', 'eProcure.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),


    ###### HOME - LANDING PAGE, BLOGS ETC ######
    url(r'^$', home_views.home, name='home'),
    url(r'^pricing/$', home_views.pricing, name='pricing'),
    url(r'^features/$', home_views.features, name='features'),
    url(r'^blog/$', home_views.blog, name='blog'),
    url(r'^blog/(?P<blog_id>\w+)/$', home_views.view_blog, name='view_blog'),
    url(r'^contact/$', home_views.contact, name='contact'),

    ###### REGISTRATION URLS (in eProc) ######
    url(r'^register/$', eProc_views.register, name='register'),
    url(r'^login/$', eProc_views.login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),

    ###### EPROCURE MODULE ######
    # Post log in URLS
    url(r'^dashboard/$', eProc_views.dashboard, name='dashboard'),
    url(r'^requisition/new/$', eProc_views.new_requisition, name='new_requisition'),
    url(r'^requisitions/$', eProc_views.requisitions, name='requisitions'),
    url(r'^requisitions/(?P<requisition_id>\w+)/$', eProc_views.view_requisition, name='view_requisition'),
    
    url(r'^purchase-orders$', eProc_views.purchaseorders, name='purchaseorders'),
    url(r'^purchase-order/new/$', eProc_views.new_purchaseorder, name='new_purchaseorder'),
    url(r'^purchase-order/(?P<po_id>\w+)/$', eProc_views.view_purchaseorder, name='view_purchaseorder'),
    url(r'^purchase-order/print/(?P<po_id>\w+)$', eProc_views.print_purchaseorder, name='print_purchaseorder'),
    # url(r'^po/receive/$', eProc_views.receive, name='receive_po'),
    
    url(r'^vendors/$', eProc_views.vendors, name='vendors'),
    url(r'^vendors/import-csv$', eProc_views.upload_vendor_csv, name='upload_vendor_csv'),
    url(r'^products/$', eProc_views.products, name='products'),
    url(r'^products/import-csv$', eProc_views.upload_product_csv, name='upload_product_csv'),

    url(r'^settings/profile/$', eProc_views.user_profile, name='user_profile'),
    url(r'^settings/company/$', eProc_views.company_profile, name='company_profile'),
    url(r'^settings/users/$', eProc_views.users, name='users'),   
    url(r'^settings/departments/$', eProc_views.departments, name='departments'),
    # url(r'^settings/taxes/$', eProc_views.taxes, name='taxes'),


]


