
# (Bug) New Req/New DD - add Order_Items incl. unit_price not updating, delete not working
# activate - url shouldnt be 127:00...


##### THREE WAY MATCH - receiving report (http://www.accountingcoach.com/blog/what-is-three-way-match)

# form errors show as messages framework
# Move form validation from view to form init

# FILES:
	# Save files uploaded/media elements (invoice, co logo, blogs etc)
	# Attach files to PO
	# Receving items - need slip/file upload (http://kb.procurify.com/?st_kb=new-procurify-receive-items)
# PO/Invoice - overinvoiced, GL codes for each line item on invoice
# Unbilled items --> allocate to specific account codes (http://kb.procurify.com/?st_kb=accounts-payable-unbilled-items)


# *****************************

# QUES:
# ****************************
# 1. WHO SHOULD SEE WHAT DOCS? Docs(Reqs/POs) etc show docs only if user is preparer or next_approver (see get_docs_by_auth). Any other situations?
# 2. See initialize_new_req_forms - Should dept dropdown be anything if SuperUser AND if in "HQ" location (today only if superuser)?
# 3. Do we want Drawdown ('Completed', 'Completed'), #TODO?? (After dd approved, when dd actually withdrawn)
# 5. Should dept be FK to company? or via locations?
# 6. Does Invoice_quantity = PO_ordered_qty or delivered quantity?
# 7. Do you have paid POs that aren't closed? So should po_template.html have if status==Closed or Open --> Mark as paid option?
# 8. Mark PO as paid or Invoice as Paid? Correspondingly mark OrderItems as paid too?
# 9. When Invoice approved/denied, what happens to order_items statuses?
# 10. DDs, Reqs (and PO/Invoices) - link to Dept? Location? or none?
# 11. Restrictions on who can add vendors/products/categories? If product not in the list and user wants to request it?

# BIG
# ****************************
# DECK
# Tests
# Form checks - Total of docs can't be negative, qty approved can't be 0 etc
# Payment
# Blogs/website
# Refactor
# Caching (eg. css files)



# NEW FEATURES
# ****************************
# PAYMENTSS:
	# https://www.procurify.com/product/pay
	# Buyer payment setup (http://kb.procurify.com/?st_kb=accounts-payable-financial-settings-set)
	# Payment method for vendor (http://kb.procurify.com/?st_kb=accounts-payable-vendor-payment-methods-set)
	# PRICING
	# API - live commodities prices with alerts
	# Wholesale prices for select products
# COST BENCHMARKS
	# Supplier Markups
	# Costs - % breakdown in same industry
	# 90% spend to 5% suppliers vs. your reality
	# #suppliers for specific product (vs. other buyers in same industry)
# Multiple plans --> manage payment and subscription options
# BULK ORDER
# NEGOTIATE (Purchaser): 
	# Bids (Proposals, quotes, specs)
	# Reverse Auction
	# Negotiate price, timelines, availib, customization
	# SLAs, contracts agreed, signed
# SERVICES/CONTRACT MANAGEMENT:
	# Obligation (product/sv from seller, payment from buyer)
	# Schedule
	# authority (who signs for both parties)
	# dispute resolution
	# Policies & procedures
# VENDOR PROFILE when vendors have username/pw 
	# user = models.OneToOneField(User, related_name="vendor_profile")
	# company = models.ForeignKey(VendorCo, related_name="users")
	# VENDOR able to create own profile based on fields buyer decides
# AUDIT LOGGGG for each item/doc



# REFINEMENTS:
# ****************************
# Fasclick menu select
# In request - choose NON CATALOG item
#  Remove qty_ordered etc into own model??
# DOc - sub and grand totals --> make into formuale, not indep fields
# INVENTORY: 
	# view_loc_inventory - how do you filter the orderItems? Right now by invoice__shippin_add but should an order Item have a shipping and billing add?
	# Make all this more efficient: inventory_list = delivered_count | neg_drawndown_count  
# Sort in datatables for dates isnt working
# Handle empty querysets (eg. no next_approver in dept for new_req)
# Email PDF
# view_Vendor - link to invoice doc
# DEPTS (from view_loc): EDIT, Spend, contracts, people etc
# Sub-categories?
# Sub-GL codes?


# LOW PRIO REFINEMENTS
# ****************************
# SPEND by BU/Dept (in Locations)
# CUSTOM DJANGO FILTERS: # Template filters (https://docs.djangoproject.com/en/1.10/howto/custom-template-tags/#writing-custom-template-filters)
# New_req - currently Next_approver is only approvers in the same dept as requester - should this change?
# Approval Routing - Select Approver by Location & Dept (http://kb.procurify.com/?st_kb=new-procurify-set-approval-routing-2)
# ADD_USER functionality in USERS when able to filter dept based on location 
# Approval routing:
	# For orders - Assign alt. approver
	# For bills/payments
# Profile no pw
# new_po_items and new_invoice_items javascript --> if unselect all items, need to deactivate add_items to PO button
# export csv for receiving report
# Move company from buyer_profile to user
# PW_change (urls.py) - # TODO: password_change isn't passing messages framework as extra_context to show pw changed success
# Each location can have multiple addresses (bill/ship)
# Remove BYERPROFILE FK to Company (only need FK for each to Location)
# DELETE USER in Locations section
# BuyerProfile - many2many with location - can have diff roles at diff locations (http://kb.procurify.com/?st_kb=accounts-payable-user-profile)
# Restricted access for AJAX requests only to me (not to anyone with an account)
# VENDOR RANKINS / SCORE CARDS
	# Vendor list with rankings (Premium feature?) (QUES: HOW TALLY THE VENDORS BETWEEN COMPANIES?)
	# Supplier Perf (Score Cards) - only for top 5% of suppliers

# ARCHIVE
# ****************************
# new_po_confirm:
    # Initialize the formsets' qty_ordered fields with qty_approved that the PO preparer can then change
    # for index, form in enumerate(po_items_formset.forms):
    #     form.fields['qty_ordered'].value = items[index].qty_approved


# ANALYSIS
	# loc_costs, loc_labels, loc_colors = [], [], []
 #    for i in list(location_spend):
 #        loc_costs.append(float(i['total_cost']))
 #        try:
 #            normalized = unicodedata.normalize('NFKD', i['invoice__shipping_add__name']).encode('ascii','ignore')
 #            loc_labels.append(normalized)
 #        except TypeError: #In case "None"
 #            loc_labels.append('Unknown')
 #        loc_colors.append(str(pastel_colors()))

      # // var locationData = {
      # //   labels: {{loc_labels|safe}},
      # //   datasets:[{
      # //     data: {{loc_costs|safe}},
      # //     backgroundColor: {{loc_colors|safe}},
      # //     label: 'Spend by Location' // for legend
      # //   }],
      # // };   