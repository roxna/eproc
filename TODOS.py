# Unbilled items --> allocate to specific account codes (http://kb.procurify.com/?st_kb=accounts-payable-unbilled-items)
##### THREE WAY MATCH - receiving report (http://www.accountingcoach.com/blog/what-is-three-way-match)

# (Bug) New Req/New DD - add Order_Items incl. unit_price not updating, delete not working
# PO/Invoice - overinvoiced, GL codes for each line item on invoice
# Issue receipts for goods??

# *****************************

# QUES:
# ****************************
# 1. WHO SHOULD SEE WHAT DOCS? Docs(Reqs/POs) etc show docs only if user is preparer or next_approver (see get_docs_by_auth). Any other situations?
# 2. See initialize_new_req_forms - Should dept dropdown be anything if SuperUser AND if in "HQ" location (today only if superuser)?
# 3. Do we want Drawdown ('Completed', 'Completed'), #TODO?? (After dd approved, when dd actually withdrawn)
# 4. Off Catalog/Vendor (rogue) spending allowed? Who can add to catalog/vendor?
# 5. Should dept be FK to company? or via locations?
# 6. Does Invoice_quantity = PO_ordered_qty or delivered quantity?
# 7. Do you have paid POs that aren't closed? So should po_template.html have if status==Closed or Open --> Mark as paid option?
# 8. Mark PO as paid or Invoice as Paid? Correspondingly mark OrderItems as paid too?
# 9. When Invoice approved/denied, what happens to order_items statuses?
# 10. DDs, Reqs (and PO/Invoices) - link to Dept? Location? or none?
# 11. Restrictions on who can add vendors/products/categories? If product not in the list and user wants to request it?
# 12. customize dashboard based on auth permissions?
# New_req - currently Next_approver is only approvers in the same dept as requester - should this change?
# view_loc_inventory - how do you filter the orderItems? Right now by invoice__shippin_add but should an order Item have a shipping and billing add?


# BIG
# ****************************
# DECK
# Tests
# Payment
# Blogs/website
# Refactor
# Caching (eg. css files)



# NEW FEATURES
# ****************************
# NOTIFICATIONS on approvals, order receipt etc
# PAYMENTSS:
	# https://www.procurify.com/product/pay
	# Buyer payment setup (http://kb.procurify.com/?st_kb=accounts-payable-financial-settings-set)
	# Payment method for vendor (http://kb.procurify.com/?st_kb=accounts-payable-vendor-payment-methods-set)
	# PRICING
	# API - live commodities prices with alerts
	# Wholesale prices for select products
	# Multiple plans --> manage payment and subscription options
# COST BENCHMARKS
	# Supplier Markups
	# Costs - % spend breakdown in same industry
	# # suppliers for specific product (vs. other buyers in same industry)
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




# REFINEMENTS:
# ****************************
# activate - url shouldnt be 127:00...
# Fasclick menu select
# Score card / vendor rating - rating/trends over time
# In request - choose NON CATALOG item
#  Remove qty_ordered etc into own model??
# DOc - sub and grand totals --> make into formuale, not indep fields
# INVENTORY: 	
	# Make all this more efficient: inventory_list = delivered_count | neg_drawndown_count  
# Sort in datatables for dates isnt working
# Handle empty querysets (eg. no next_approver in dept for new_req)
# Email PDF
# view_Vendor - link to invoice doc
# DEPTS (from view_loc): EDIT, Spend, contracts, people etc
# Sub-categories?
# Sub-GL codes?
# AUDIT LOGGGG for each item/doc


# LOW PRIO REFINEMENTS
# ****************************
# SPEND by BU/Dept (in Locations)
# CUSTOM DJANGO FILTERS: # Template filters (https://docs.djangoproject.com/en/1.10/howto/custom-template-tags/#writing-custom-template-filters)
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
# VENDOR RANKINGS / SCORE CARDS
	# Vendor list with rankings (Premium feature?) (QUES: HOW TALLY THE VENDORS BETWEEN COMPANIES?)
	# Supplier Perf (Score Cards) - only for top 5% of suppliers
# forms 
	# move errors to messages framework (view_location)
	# Add checks in views - Total of docs can't be negative, qty approved can't be 0 etc
	# Form errors not showing (view_location)
# keep modal up on error - https://www.reddit.com/r/django/comments/4souit/how_to_keep_a_modal_window_open_if_a_validation/


