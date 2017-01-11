

# console - custom.js cant find
# Edit product price
# APPROVAL ROUTING (New Req): APprovers only on Dept selected (queryset not updating for dept/next_approver)
# Save files uploaded/media elements (invoice, co logo, blogs etc)
# Refactor
#  Change all 'backs' to clearly state where going
# (Bug) New Req/New DD - add Order_Items
# Order_Items into individual entries (new PO): Num not delivered is created into new Item linked to same PR
# # TODO CLEANER IMPLEMENTATION OF get_docu_by_status(utils.py)
	# pending_requisitions = requisitions.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Pending')
    # pending_pos = pos.annotate(latest_update=Max('status_updates__date')).filter(status_updates__value='Pending')


# Invoices
	# ('Pending', 'Pending'), #TODO Update: On invoice creation    
    # ('Cancelled', 'Cancelled'), #TODO
    # ('Paid', 'Paid'),  #TODO: Updated on view_invoice/1
# DD
	# ('Completed', 'Completed'), #TODO


# *****************************

# QUES:
# ****************************
# 1. Docs(Reqs/POs) etc show docs only if user is preparer or next_approver (see get_docs_by_auth). Any other situations?

# BIG
# ****************************
# Tests
# Payment
# Blogs/website
# Caching (eg. css files)


# NEW FEATURES
# ****************************
# PRICING
	# API - live commodities prices with alerts
	# Wholesale prices for select products
# COST BENCHMARKS
	# Costs - % breakdown in same industry
	# 90% spend to 5% suppliers vs. your reality
# VENDOR RANKINS / SCORE CARDS
	# Vendor list with rankings (Premium feature?) (QUES: HOW TALLY THE VENDORS BETWEEN COMPANIES?)
	# Supplier Perf (Score Cards) - only for top 5% of suppliers
# Multiple plans --> manage payment and subscription options
# In request - choose NON CATALOG item
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


# REFINEMENTS:
# ****************************
# Fasclick menu select
# INVENTORY: 
	# view_loc_inventory - how do you filter the orderItems? Right now by invoice__shippin_add but should an order Item have a shipping and billing add?
	# Make all this more efficient: inventory_list = delivered_count | neg_drawndown_count  
# Mgr (get_latest_status)
# Email PDF
# view_Vendor - link to invoice doc
# BuyerProfile - many2many with location - can have diff roles at diff locations (http://kb.procurify.com/?st_kb=accounts-payable-user-profile)
# DEPTS (from view_loc): EDIT, Spend, contracts, people etc

# LOW PRIO REFINEMENTS
# ****************************
# Template filters (https://docs.djangoproject.com/en/1.10/howto/custom-template-tags/#writing-custom-template-filters)
# New_req - currently Next_approver is only approvers in the same dept as requester - should this change?
# Approval Routing - Select Approver by Location & Dept (http://kb.procurify.com/?st_kb=new-procurify-set-approval-routing-2)
# ADD_USER functionality in USERS when able to filter dept based on location
# Approver - Assign alt. approver
# Profile no pw
# Move company from buyer_profile to user
# PW_change (urls.py) - # TODO: password_change isn't passing messages framework as extra_context to show pw changed success
# Each location can have multiple addresses (bill/ship)
# Remove DEPT and BYERPROFILE FK to Company (only need FK for each to Location)
# DELETE USER in Locations section


# ARCHIVE
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

