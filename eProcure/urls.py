from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()
from django.contrib.auth.views import login, logout
from django.contrib.auth import views as auth_views
from home import views as home_views
from eProc import views as eProc_views
from eProc.forms import LoginForm


urlpatterns=[

    url(r'^admin/', include(admin.site.urls)),

    ##########################################
    ####  HOME - LANDING PAGE, BLOGS ETC  ####
    ##########################################

    # GENERAL
    url(r'^$', home_views.home, name='home'),
    url(r'^pricing/$', home_views.pricing, name='pricing'),
    url(r'^features/$', home_views.features, name='features'),
    url(r'^blog/$', home_views.blog, name='blog'),
    url(r'^blog/(?P<blog_id>\w+)/(?P<blog_slug>[\w-]+)/$', home_views.view_blog, name='view_blog'), 
    url(r'^faqs/$', home_views.faqs, name='faqs'),
    url(r'^contact/$', home_views.contact, name='contact'),
    url(r'^success/$', home_views.success, name='success'),
    
    # LEGAL
    url(r'^terms/$', home_views.terms, name='terms'),
    url(r'^privacy-policy/$', home_views.privacy_policy, name='privacy_policy'),

    ###### REGISTRATION URLS (in eProc) ######
    url(r'^register/$', eProc_views.register, name='register'),    
    url(r'^activate/$', eProc_views.activate, name='activate'),
    url(r'^login/$', login, {'authentication_form': LoginForm, }, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^thankyou/$', eProc_views.thankyou, name='thankyou'),
    
    # Reset Password - https://docs.djangoproject.com/en/1.8/_modules/django/contrib/auth/views/
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^password_change/$', auth_views.password_change, {'post_change_redirect': 'user_profile'}, name='password_change'),
    # url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),


    ############################################
    ##      EPROC MODULE  (login required)    ##
    ###########################################

    # NOTE: If change the urls (not url names) here, make sure to update in base_portal for active highlighting
    
    url(r'^get-started/$', eProc_views.get_started, name='get_started'),
    url(r'^dashboard/$', eProc_views.dashboard, name='dashboard'),
    url(r'^trial-over-subscribe-now/$', eProc_views.trial_over_not_subscribed, name='trial_over_not_subscribed'),
    url(r'^subscribe/$', eProc_views.subscribe, name='subscribe'),
        
    url(r'^requisitions/', include([
        url(r'^new/$', eProc_views.new_requisition, name='new_requisition'),
        url(r'^$', eProc_views.requisitions, name='requisitions'),
        url(r'^view/(?P<requisition_id>\w+)/$', eProc_views.view_requisition, name='view_requisition'),
        url(r'^print/(?P<requisition_id>\w+)$', eProc_views.print_requisition, name='print_requisition'),
    ])),
    
    url(r'^purchase-orders/', include([
        url(r'^new/select-items/$', eProc_views.new_po_items, name='new_po_items'),
        url(ur'^new/confirm\w*/$', eProc_views.new_po_confirm, name='new_po_confirm'),
        url(r'^$', eProc_views.purchaseorders, name='purchaseorders'),
        url(r'^view/(?P<po_id>\w+)/$', eProc_views.view_po, name='view_po'),
        url(r'^print/(?P<po_id>\w+)$', eProc_views.print_po, name='print_po'),            
        url(r'^items/(?P<po_id>\w+)/$', eProc_views.po_orderitems, name='po_orderitems'), #AJAX request on new_invoice (see custom.js)
    ])),

    url(r'^receive/', include([
        url(r'^$', eProc_views.receive_pos, name='receive_pos'),
        url(r'^(?P<po_id>\w+)/$', eProc_views.receive_po, name='receive_po'),
        
    ])),

    url(r'^accounts-payable/', include([
        url(r'^invoices/', include([
            url(r'^$', eProc_views.invoices, name='invoices'),    
            url(r'^new/select-items/$', eProc_views.new_invoice_items, name='new_invoice_items'),
            url(r'^new/confirm\w*/$', eProc_views.new_invoice_confirm, name='new_invoice_confirm'),
            url(r'^view/(?P<invoice_id>\w+)/$', eProc_views.view_invoice, name='view_invoice'),
            url(r'^print/(?P<invoice_id>\w+)$', eProc_views.print_invoice, name='print_invoice'),
            url(r'^(?P<vendor_id>\w+)/$', eProc_views.vendor_invoices, name='vendor_invoices'), #AJAX request (see custom.js)
        ])),
        url(r'^unbilled-items/$', eProc_views.unbilled_items, name='unbilled_items'),
        url(r'^receiving-summary/$', eProc_views.receiving_summary, name='receiving_summary'),
    ])),    

    url(r'^inventory/', include([
        url(r'^$', eProc_views.inventory, name='inventory'),
        url(r'^(?P<location_id>\w+)/(?P<location_name>[\w-]+)/$', eProc_views.view_location_inventory, name='view_location_inventory'),
    ])),

    url(r'^drawdowns/', include([
        url(r'^new/$', eProc_views.new_drawdown, name='new_drawdown'),
        url(r'^$', eProc_views.drawdowns, name='drawdowns'),            
        url(r'^view/(?P<drawdown_id>\w+)/$', eProc_views.view_drawdown, name='view_drawdown'),
        url(r'^print/(?P<drawdown_id>\w+)/$', eProc_views.print_drawdown, name='print_drawdown'),
        url(r'^call/$', eProc_views.call_drawdowns, name='call_drawdowns'),
        url(r'^call/(?P<drawdown_id>\w+)/$', eProc_views.call_drawdown, name='call_drawdown'),
    ])),

    url(r'^reports/', include([
        url(r'^spend-by-location-department/$', eProc_views.spend_by_location_dept, name='spend_by_location_dept'),
        url(r'^spend-by-product-category/$', eProc_views.spend_by_product_category, name='spend_by_product_category'),
        url(r'^spend-by-entity/$', eProc_views.spend_by_entity, name='spend_by_entity'),
        url(r'^industry-benchmarks/$', eProc_views.industry_benchmarks, name='industry_benchmarks'),
    ])),    

    url(r'^price-alerts/', include([
        url(r'^$', eProc_views.price_alerts, name='price_alerts'),
        url(r'^current-price/(?P<commodity_id>\w+)/$', eProc_views.get_commodity_current_price, name='get_commodity_current_price'),  # AJAX request to populate the price_alerts table
    ])),
    url(r'^settings/', include([
        url(r'^$', eProc_views.settings, name='settings'),
        url(r'^profile/$', eProc_views.user_profile, name='user_profile'),
        url(r'^company/$', eProc_views.company_profile, name='company_profile'),
        url(r'^users/$', eProc_views.users, name='users'),
        url(r'^locations/$', eProc_views.locations, name='locations'),
        url(r'^vendors/', include([
            url(r'^$', eProc_views.vendors, name='vendors'),
            url(r'^(?P<vendor_id>\w+)/(?P<vendor_name>[\w-]+)/$', eProc_views.view_vendor, name='view_vendor'),
            url(r'^import-csv$', eProc_views.upload_vendor_csv, name='upload_vendor_csv'),
            url(r'^rating/(?P<vendor_id>\w+)/(?P<vendor_name>[\w-]+)/$', eProc_views.rate_vendor, name='rate_vendor'), 
            url(r'^unbilled-items/(?P<vendor_id>\w+)/$', eProc_views.unbilled_items_by_vendor, name='unbilled_items_by_vendor'), #AJAX REQUEST in new_invoice_items to get unbilled_items for specific vendor
        ])),
        url(r'^products/', include([
            url(r'^$', eProc_views.products, name='products'),
            url(r'^import-csv/$', eProc_views.upload_product_csv, name='upload_product_csv'),
            url(r'^bulk/$', eProc_views.products_bulk, name='products_bulk'),
            url(r'^(?P<product_id>\w+)/$', eProc_views.product_details, name='product_details'), #AJAX request        
        ])),
        url(r'^categories/$', eProc_views.categories, name='categories'),
        url(r'^(?P<location_id>\w+)/(?P<location_name>[\w-]+)/$', eProc_views.view_location, name='view_location'),
        url(r'^account-codes/$', eProc_views.account_codes, name='account_codes'),
        url(r'^approval-routing/$', eProc_views.approval_routing, name='approval_routing'),
        # url(r'^taxes/$', eProc_views.taxes, name='taxes'),
        url(r'^notifications/mark_as_read$', eProc_views.mark_notifications_as_read, name='mark_notifications_as_read'),
    ])),      

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     # static files (images, css, javascript, etc.)
#     urlpatterns += patterns('',
#         (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
#         'document_root': settings.MEDIA_ROOT}))


