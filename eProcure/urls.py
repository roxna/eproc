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
    
    # url(r'^po/new/$', views.create, name='create_po'),
    # url(r'^po/receive/$', views.receive, name='receive_po'),
    
    # url(r'^vendors/$', views.documents, name='vendors'),
    # url(r'^vendors/new/$', views.documents, name='new_vendor'),
    # url(r'^products/$', views.documents, name='products'),
    # url(r'^products/new/$', views.documents, name='new_product'),

    # url(r'^settings/user-profile/$', views.user_profile, name='user_profile'),
    # url(r'^settings/company-profile/$', views.company_profile, name='company_profile'),
    url(r'^settings/users/$', views.users, name='users'),   
    url(r'^settings/user/new/$', views.new_user, name='new_user'),    
    url(r'^settings/departments/$', views.departments, name='departments'),
    # url(r'^settings/taxes/$', views.taxes, name='taxes'),


]