from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from django.contrib.auth.views import logout
from eProc import views

urlpatterns=[
    # Examples:
    # url(r'^$', 'eProcure.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),

    # Post log in URLS
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^requisition/new/$', views.new_requisition, name='new_requisition'),
    url(r'^requisitions/$', views.requisitions, name='requisitions'),
    url(r'^requisitions/(?P<requisition_id>\w+)/$', views.view_requisition, name='view_requisition'),
    
    url(r'^purchaseorders$', views.purchaseorders, name='purchaseorders'),
    url(r'^purchaseorder/new/$', views.new_purchaseorder, name='new_purchaseorder'),
    url(r'^purchaseorder/(?P<po_id>\w+)/$', views.view_purchaseorder, name='view_purchaseorder'),
    url(r'^purchaseorder/print/(?P<po_id>\w+)$', views.print_purchaseorder, name='print_purchaseorder'),
    # url(r'^po/receive/$', views.receive, name='receive_po'),
    
    url(r'^vendors/$', views.vendors, name='vendors'),
    # url(r'^vendors/new/$', views.documents, name='new_vendor'),
    url(r'^products/$', views.products, name='products'),

    url(r'^settings/profile/$', views.user_profile, name='user_profile'),
    url(r'^settings/company/$', views.company_profile, name='company_profile'),
    url(r'^settings/users/$', views.users, name='users'),   
    url(r'^settings/departments/$', views.departments, name='departments'),
    # url(r'^settings/taxes/$', views.taxes, name='taxes'),


]


