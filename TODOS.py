# EDITS: View_Location, Moved Depts & (Add) User to under Locations (from Settings), Simplified Co_Profile


# TODO: ADD_USER functionality in USERS when able to filter dept based on location

# LOCATIONS : Inventory - by each location (Shipping Add) 

# Edit product price

###### APPROVAL ROUTING - who requesters can go to, threshold $ APPROVAL
# http://kb.procurify.com/?st_kb=new-procurify-set-approval-routing-2
# New Req: APproveres only on Dept selected
#  Approval routing in get_started

# Save files uploaded/media elements (invoice, co logo, blogs etc)

#  VENDOR RANKINGS 
#  See vendor list with rankings (Premium feature?) (QUES: HOW TALLY THE VENDORS BETWEEN COMPANIES?)
# Supplier Perf (Score Cards) - only for top 5% of suppliers

# LATER
# VIEW DEPT: EDIT, Spend, contracts, people etc OR # Edit dept formset (see new_dd)

# - Profile no pw
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
# Approver - Assign alt. approver
# Each location can have multiple addresses (bill/ship)
# Remove DEPT and BYERPROFILE FK to Company (only need FK for each to Location)
# DELETE USER in Locations section

