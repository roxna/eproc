
# DEPTS (from view_loc): EDIT, Spend, contracts, people etc, PRICE_ALERTS
# Change all choicefields to numbers


# Update charts to daily
# Guidoism.objects \
#     # get specific dates (not hours for example) and store in "created" 
#     .extra({'created':"date(created)"})
#     # get a values list of only "created" defined earlier
#     .values('created')
#     # annotate each day by Count of Guidoism objects
#     .annotate(created_count=Count('id'))

# Stripe/own db?? - subscription about to expire - send email
# django smart_selects for dept/location http://stackoverflow.com/questions/35242412/filter-choices-in-form-fields-based-on-selected-items-in-fields-of-the-same-form

# *****************************

# QUES:
# ****************************
# 1. WHO SHOULD SEE WHAT DOCS? Docs(Reqs/POs) etc show docs only if user is preparer or next_approver (see get_docs_by_auth). Any other situations?
# 2. See initialize_new_req_forms - Should dept dropdown be anything if SuperUser AND if in "HQ" location (today only if superuser)?
# 4. Off Catalog/Vendor (rogue) spending allowed? Who can add to catalog/vendor?
# 5. Should dept be FK to company? or via locations?
# 6. Does Invoice_quantity = PO_ordered_qty or delivered quantity?
# 7. Do you have paid POs that aren't closed? So should po_template.html have if status==Closed or Open --> Mark as paid option?
# 8. Mark PO as paid or Invoice as Paid? Correspondingly mark OrderItems as paid too?
# 10. DDs, Reqs (and PO/Invoices) - link to Dept? Location? or none?
# 11. Restrictions on who can add vendors/products/categories? If product not in the list and user wants to request it?
# 12. customize dashboard based on auth permissions?
# New_req - currently Next_approver is only approvers in the same dept as requester - should this change?
# view_loc_inventory - how do you filter the orderItems? Right now by invoice__shippin_add but should an order Item have a shipping and billing add?
# 13. Issue receipts for goods???

# BIG
# ****************************
# DECK
# Tests
# Caching (eg. css files)



# NEW FEATURES
# ****************************
# PAYMENTS FOR BUYERCO:
	# https://www.procurify.com/product/pay
	# Buyer payment setup (http://kb.procurify.com/?st_kb=accounts-payable-financial-settings-set)
	# Payment method for vendor (http://kb.procurify.com/?st_kb=accounts-payable-vendor-payment-methods-set)
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

# Reqs - marked as 'Executed'
# Can receive items that are in an Open PO OR in an Approved Req that's not linked to a PO
	# Small items bought by cash must have a Req but not necessarily a PO
	# However, they must be added to stock/inventory 
	# Have a DELIVERY CHALLAN, Req marked as 'Executed/Completed'

# Dashboard for average user based on role (if AP, show invoices not requisitions)
# Unbilled v2 --> allocate to specific account codes (http://kb.procurify.com/?st_kb=accounts-payable-unbilled-items)
# Images - catalog items (csv upload)
# activate - url shouldnt be 127:00...
# Score card / vendor rating - rating/trends over time
# In request - choose NON CATALOG item
# Make all queries more efficient (eg Inventory drawdownlist | inventoryList etc)
# Sort in datatables for dates isnt working
# Handle empty querysets (eg. no next_approver in dept for new_req)
# Email PDF
# Sub-categories?
# Sub-GL codes?
# Add Controller, Branch Manager: http://kb.procurify.com/?st_kb=new-procurify-add-new-users-need-update
# addWhatFix
# AUDIT LOGGGG for each item/doc
# 1 item - multiple POs? Order Items with ordered_qty < approved_qty from the company, 
	# update model to M2M field, new_po_confirm, current_status - partially ordered??


# LOW PRIO REFINEMENTS
# ****************************
# SPEND by BU/Dept (in Locations)
# Approval Routing - Select Approver by Location & Dept (http://kb.procurify.com/?st_kb=new-procurify-set-approval-routing-2)
# Refactor - DD = Requisition (item_table)
# ADD_USER functionality in USERS when able to filter dept based on location 
# Approval routing:
	# For orders - Assign alt. approver
	# For bills/payments
# export csv for receiving report
# Move company from buyer_profile to user / # Remove BYERPROFILE FK to Company (only need FK for each to Location)
# PW_change (urls.py) - # TODO: password_change isn't passing messages framework as extra_context to show pw changed success
# Each location can have multiple addresses (bill/ship)
# DELETE USER in Locations section
# BuyerProfile - many2many with location - can have diff roles at diff locations (http://kb.procurify.com/?st_kb=accounts-payable-user-profile)
# Restricted access for AJAX requests only to me (not to anyone with an account)
# VENDOR RANKINGS / SCORE CARDS
	# Vendor list with rankings (Premium feature?) (QUES: HOW TALLY THE VENDORS BETWEEN COMPANIES?)
	# Supplier Perf (Score Cards) - only for top 5% of suppliers
# keep modal up on error - https://www.reddit.com/r/django/comments/4souit/how_to_keep_a_modal_window_open_if_a_validation/



# NOTES:
# cd Desktop/eProc/eProc
# workon eProcure
# Start server: pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
# psql postgres then create database dbname; then \connect dbname
# python manage.py migrate --run-syncdb


