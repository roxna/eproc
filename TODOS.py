# Approval_routing/thresholds, Docs (Reqs, POs, Invoices, DDs) only show if you're preparer/approver, 404 & 500 handlers/templates
# APPROVAL ROUTING (New Req): APproveres only on Dept selected (queryset not updating for dept/next_approver)


# LOCATIONS : Inventory - by each location (Shipping Add) 
# Edit product price

# Save files uploaded/media elements (invoice, co logo, blogs etc)
# VIEW DEPT: EDIT, Spend, contracts, people etc OR # Edit dept formset (see new_dd)

# Your pending actions (dashboard)

# *****************************

# BIG
# **********
# Tests
# Payment
# Refactor
# Order_Items into individual entries (new PO): Num not delivered is created into new Item linked to same PR
# Blogs/website


# NEW FEATURES
# **********
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
# **********
# Fasclick menu select
# Mgr (get_latest_status)
# (Bug) New Req/New DD - add Order_Items
# Email PDF
# view_Vendor - link to invoice doc
# BuyerProfile - many2many with location - can have diff roles at diff locations (http://kb.procurify.com/?st_kb=accounts-payable-user-profile)


# LOW PRIO REFINEMENTS
# **********
# New_req - currently Next_approver is only approvers in the same dept as requester - should this change?
# Approval Routing - Select Approver by Location & Dept (http://kb.procurify.com/?st_kb=new-procurify-set-approval-routing-2)
# ADD_USER functionality in USERS when able to filter dept based on location
# Approver - Assign alt. approver
# Profile no pw
# PW_change (urls.py) - # TODO: password_change isn't passing messages framework as extra_context to show pw changed success
# Each location can have multiple addresses (bill/ship)
# Remove DEPT and BYERPROFILE FK to Company (only need FK for each to Location)
# DELETE USER in Locations section

