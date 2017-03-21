from django import forms
from django.conf import settings as conf_settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.db.models import Count
from django.forms import ModelForm
from eProc.models import *
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, HTML
# import pytz

####################################
###         REGISTRATION         ### 
####################################

class RegisterUserForm(UserCreationForm):
    full_name = forms.CharField(required=True)
    username = forms.CharField(required=True) 
    email = forms.EmailField(required=True)
    # profile_pic = forms.ImageField(label="Profile Picture", required=False)
    
    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['password2'].required = False
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('full_name', css_class='col-md-6'),
                Div('username', css_class='col-md-6'),
                css_class='row',
            ),
            Div(
                Div('email', css_class='email col-md-6'),
                Div('password1', css_class='col-md-6'),
                css_class='row',
            ),            
        )
        self.helper.form_tag = False

    class Meta:
        model = User
        fields = ("username", "email", "password1")

    def clean_username(self):        
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    def save(self, commit=True):
        user = super(RegisterUserForm, self).save(commit=False)        
        try:
            user.first_name, user.last_name = self.cleaned_data["full_name"].split()
        except ValueError:
            # If there's no space to split on
            user.first_name = self.cleaned_data["full_name"]
        user.password2 = self.cleaned_data["password1"]
        user.is_active = False  #User not active until activate account through email
        if commit:
            user.save()
        return user

# class SubscriptionForm(ModelForm):
#     pass

#     class Meta:
#         model = Subscription
#         fields = ('plan', )


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

# Didn't use Django UserChangeForm because that requires PW
class ChangeUserForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ChangeUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False        
        self.helper.layout = Layout(
            Field('username', css_class='form-control', readonly=True),
            Field('email', css_class='form-control', readonly=True),
        )
        self.helper.form_tag = False

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)


# CREATING A USER WITH A TEMP PASSWORD
class AddUserForm(forms.Form):  
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True) 
    title = forms.CharField(required=False)
    email = forms.EmailField(required=True, label="<i class='fa fa-envelope'></i> Email")  

    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(
        Div(
            Div('first_name', css_class='col-md-6'),
            Div('last_name', css_class='col-md-6'),
            css_class='row',
        ),
        Div(
            Div('title', css_class='col-md-6'),
            Div('email', css_class='col-md-6'),
            css_class='row',
        )
    )

    def get_username(self):
        return self.cleaned_data['first_name'].lower()+'_'+self.cleaned_data['last_name'].lower()

    def clean_username(self):
        try:
            User.objects.get(username=self.get_username())
        except User.DoesNotExist:
            return self.get_username()
        raise forms.ValidationError('Username already in use')

    def clean_email(self):
        try:
            User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError('Email already in use')

    def save(self):
        # Check that there isn't another user with same username or email
        if self.clean_username() and self.clean_email():
            user = User.objects.create_user(username=self.clean_username(),
                                            email=self.cleaned_data['email'],
                                            password='temppw',)        
            user.first_name=self.cleaned_data['first_name']
            user.last_name=self.cleaned_data['last_name']
            user.title=self.cleaned_data['title']
            user.is_active=False
            user.save()
            return user


####################################
###        COMPANY FORMS         ### 
####################################

class BuyerProfileForm(ModelForm):  
    role = forms.ChoiceField(conf_settings.ROLES, required=True, label="<i class='fa fa-user'></i> Role")
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label="<i class='fa fa-building'></i> Department")

    def __init__(self, *args, **kwargs):
        super(BuyerProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                # Div('location', css_class='col-md-6'),
                Div('department', css_class='col-md-6'),
                Div('role', css_class='col-md-6'),
                css_class='row',
            ),
        )

    class Meta:
        model = BuyerProfile
        fields = ("role", "department",)
        

class BuyerCoForm(forms.ModelForm):
    name = forms.CharField(required=True)
    industry = forms.ChoiceField(conf_settings.INDUSTRY_CHOICES, required=True, )
    currency = forms.ChoiceField(conf_settings.CURRENCIES, required=True, initial='USD')
    logo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(BuyerCoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-12'),
                css_class='row',
            ),
            Div(
                Div('industry', css_class='col-md-6'),
                Div('currency', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False

    class Meta:
        model = BuyerCo
        fields = ('name', 'industry', 'currency')

# Used to create a new Vendor 
class VendorCoForm(ModelForm):
    name = forms.CharField(required=True, label="<i class='fa fa-building'></i> Vendor Name")
    vendorID = forms.CharField(required=False, label="<i class='fa fa-id-card'></i> Vendor ID")
    contact_rep = forms.CharField(required=False, label="<i class='fa fa-user'></i> Contact Rep")
    website = forms.URLField(required=False, label="<i class='fa fa-globe'></i> Website")
    comments = forms.CharField(required=False, label="<i class='fa fa-sticky-note'></i> Comments")

    def __init__(self, *args, **kwargs):
        super(VendorCoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('vendorID', css_class='col-md-6'),
                css_class='row',
            ),
            Div(
                Div('contact_rep', css_class='col-md-6'),
                Div('website', css_class='col-md-6'),
                css_class='row',
            ),
            Div(
                Div('comments', css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        model = VendorCo
        fields = ("name", "contact_rep", "website", "vendorID", "comments")


# Used for the dropdown selection in new_invoice_items view
class VendorForm(forms.Form):
    name = forms.ModelChoiceField(required=True, queryset=VendorCo.objects.none(), label='')

# Used to rank a Vendor
class VendorRatingForm(ModelForm):
    category = forms.ChoiceField(conf_settings.CATEGORIES, required=True)
    # category = forms.ChoiceField(conf_settings.CATEGORIES, required=True, widget=forms.Select(attrs={'readonly': 'true', 'disabled':'true'}))
    comments = forms.CharField(required=False,)

    def __init__(self, *args, **kwargs):
        super(VendorRatingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('category', css_class='col-md-4'),
                Div('score', css_class='col-md-2'),
                Div('comments', css_class='col-md-6'),
                css_class='row',
            ),
        )
    # Ensure readonly/disabled 'category' field is not edited by users on submit
    # def clean_category(self):        
    #     if self.instance:
    #         return self.instance.category
    #     else: 
    #         return self.cleaned_data['category']

    class Meta:
        model = Rating
        fields = ("score", "category", "comments")

class LocationForm(ModelForm):
    name = forms.CharField(required=True, label="Location Name")
    loc_type = forms.ChoiceField(conf_settings.LOCATION_TYPES, label="<i class='fa fa-map-marker'></i> Location Type")
    address1 = forms.CharField(required=True, label="<i class='fa fa-home'></i> Address Line 1")
    address2 = forms.CharField(required=False, label="<i class='fa fa-home'></i> Address Line 2")
    city = forms.CharField(required=True, label="<i class='fa fa-location-arrow'></i> City")
    state = forms.CharField(required=True, label="<i class='fa fa-location-arrow'></i> State")
    zipcode = forms.CharField(required=True, label="<i class='fa fa-location-arrow'></i> Zip Code")
    country = forms.ChoiceField(conf_settings.COUNTRIES, required=True, initial='USA', label="<i class='fa fa-globe'></i> Country")
    phone = forms.CharField(required=False, label="<i class='fa fa-phone'></i> Phone Number")
    email = forms.EmailField(required=False, label="<i class='fa fa-envelope'></i> Email")
    
    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('loc_type', css_class='col-md-6'),
                css_class='row',
            ),
            Div(
                Div('address1', css_class='col-md-6'),
                Div('address2', css_class='col-md-6'),
                css_class='row',
            ),
            Div(
                Div('city', css_class='col-md-6'),
                Div('state', css_class='col-md-6'),
                css_class='row',
            ),
            Div(
                Div('zipcode', css_class='col-md-6'),
                Div('country', css_class='col-md-6'),
                css_class='row',
            ),
            Div(
                Div('email', css_class='col-md-6'),
                Div('phone', css_class='col-md-6'),
                css_class='row',
            ),
        )

    class Meta:
        model = Location
        fields = ('name', 'loc_type', 'address1', 'address2', 'city', 'state', 'country', 'zipcode', 'phone', 'email')        

####################################
###       SETTINGS FORMS         ### 
####################################

class DepartmentForm(ModelForm):
    name = forms.CharField(required=True)
    budget = forms.DecimalField(min_value=0, label="Annual budget")

    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('budget', css_class='col-md-6'),
                css_class='row',
            ),
        )

    class Meta:
        model = Department
        fields = ("name", "budget")

class TaxForm(ModelForm):
    percent = forms.DecimalField(min_value=0, label="Percent (%)", help_text='Input the percent value only, without "%"s')

    def __init__(self, *args, **kwargs):
        super(TaxForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('percent', css_class='col-md-6'),
                css_class='row',
            ),
        )

    class Meta:
        model = Tax
        fields = ("name", "percent")

class AccountCodeForm(ModelForm):
    expense_type = forms.ChoiceField(conf_settings.EXPENSE_TYPES, required=True, )
    departments = forms.ModelMultipleChoiceField(queryset=Department.objects.all(), required=True, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(AccountCodeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = AccountCode
        fields = ("code", "name", "expense_type", "departments")
        widgets = {
            'departments': forms.CheckboxSelectMultiple(),
        }

class CategoryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False        

    class Meta:
        model = Category
        fields = ("name", "code")


####################################
###   PRODUCT/CATALOG FORM       ### 
####################################

class CatalogItemForm(ModelForm):
    name = forms.CharField(required=True)
    sku = forms.CharField(required=True)    
    min_threshold = forms.IntegerField(min_value=0, help_text='Min. stock level before alert triggered', required=False)
    max_threshold = forms.IntegerField(min_value=0, help_text='Max. stock level before alert triggered', required=False)
    unit_price = forms.DecimalField(required=True, min_value=0)
    unit_type = forms.CharField(required=True)
    # currency = forms.ChoiceField(conf_settings.CURRENCIES, required=True, initial='USD')
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    vendor_co = forms.ModelChoiceField(queryset=VendorCo.objects.all(), label="Preferred Vendor")

    def __init__(self, *args, **kwargs):
        super(CatalogItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-sm-12 col-md-8'),                
                Div('sku', css_class='col-md-4'),
                css_class='row',
            ),
            Div(
                Div('desc', css_class='col-md-12'),                
                css_class='row',
            ),            
            Div(
                Div('unit_price', css_class='col-md-4'),
                Div('unit_type', css_class='col-md-4'),
                Div('category', css_class='col-md-4'),
                css_class='row',
            ),
            Div(
                Div('vendor_co', css_class='col-md-4'),
                Div('min_threshold', css_class='col-md-2'),
                Div('max_threshold', css_class='col-md-2'),
                Div('image', css_class='col-md-4'),
                css_class='row',
            ),                        
        )

    def clean(self):
        cleaned_data = super(CatalogItemForm, self).clean()
        min_threshold = self.cleaned_data['min_threshold']
        max_threshold = self.cleaned_data['max_threshold']
        if min_threshold > max_threshold and max_threshold is not None:
            self.add_error('min_threshold', 'Min. threshold must be less than Max')
        return cleaned_data

    class Meta:
        model = CatalogItem
        fields = ('name', 'sku', 'desc', 'image', 'min_threshold', 'max_threshold', 'unit_price', 'unit_type', 'category', 'vendor_co')


class CatalogItemRequestForm(ModelForm):
    currency = forms.ChoiceField(conf_settings.CURRENCIES, required=True, initial='USD')
    unit_price = forms.DecimalField(required=False, min_value=0, label="Max price")
    unit_type = forms.CharField(required=True, initial='each')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Closest matching category")

    def __init__(self, *args, **kwargs):
        super(CatalogItemRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-sm-12 col-md-6'),                
                Div('category', css_class='col-sm-12 col-md-6'),
                css_class='row',
            ),       
            Div(
                Div('desc', css_class='col-md-12'),
                css_class='row',
            ),            
            Div(
                Div('currency', css_class='col-md-4'),
                Div('unit_price', css_class='col-md-4'),
                Div('unit_type', css_class='col-md-4'),
                css_class='row',
            ),
        )

    class Meta:
        model = CatalogItemRequest
        fields = ('name', 'desc', 'currency', 'unit_price', 'unit_type', 'category',)

####################################
###      ORDER ITEM FORMS        ### 
####################################

class NewReqItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), required=True)    
    price_requested = forms.DecimalField(required=True)    
    qty_requested = forms.IntegerField(required=True, min_value=1)
    account_code = forms.ModelChoiceField(queryset=AccountCode.objects.all(), required=True)
    comments_requested = forms.CharField(required=False,)

    def __init__(self, *args, **kwargs):
        super(NewReqItemForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('product', css_class='item-product col-md-2'),
                Div('qty_requested', css_class='item-quantity col-md-2'),
                Div('price_requested', css_class='item-price col-md-2'),
                Div('account_code', css_class='item-account-code col-md-2'),
                Div('comments_requested', css_class='item-comments col-md-3'),
                HTML('<a class="delete col-md-1" href="#"><i class="fa fa-trash"></i></a>'),
                css_class='row',
            ),
        )

    class Meta:
        model = OrderItem
        fields = ("product", "qty_requested", "price_requested", "account_code", "comments_requested")

class ApproveReqItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), widget=forms.Select(attrs={'readonly':'true'}))
    price_approved = forms.DecimalField(widget=forms.TextInput(attrs={'readonly':'true'}), label="Price")
    qty_requested = forms.IntegerField(widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Requested')
    qty_approved = forms.IntegerField(required=True, label='Approved')
    comments_requested = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Request Comments')
    comments_approved = forms.CharField(required=False, label='Approval Comments')


    def __init__(self, *args, **kwargs):
        super(ApproveReqItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div( 
                Div('product', css_class='col-md-2'),
                Div('price_approved', css_class='col-md-1'),
                Div('qty_requested', css_class='col-md-1'),                
                Div('comments_requested', css_class='col-md-3'),
                Div('qty_approved', css_class='col-md-2'),
                Div('comments_approved', css_class='col-md-3'),
                css_class='row',
            ),
        )  

    # Ensure readonly 'product' field (Select/ChoiceField) is not editable by users 
    # More here: http://stackoverflow.com/questions/324477/in-a-django-form-how-do-i-make-a-field-readonly-or-disabled-so-that-it-cannot   
    def clean_product(self):
        if self.instance:
            return self.instance.product
        else: 
            return self.cleaned_data['product']

    def clean(self):
        cleaned_data = super(ApproveReqItemForm, self).clean()
        qty_approved = self.cleaned_data['qty_approved']
        qty_requested = self.cleaned_data['qty_requested']
        if qty_approved <= 0:
            self.add_error('qty_approved', 'Quantity must be greater than 0')
        elif qty_approved > qty_requested:
            self.add_error('qty_approved', 'Only '+str(qty_requested)+' items have been requested')
        return cleaned_data

    class Meta:
        model = OrderItem
        fields = ('product', 'price_approved', 'qty_requested', 'qty_approved', 'comments_requested', 'comments_approved')
        

class NewPOItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), widget=forms.Select(attrs={'readonly':'true'}))
    qty_approved = forms.IntegerField(label='Qty Approved', widget=forms.TextInput(attrs={'readonly':'true'}))
    qty_ordered = forms.IntegerField(required=True, min_value=1, label='Qty To Order')
    price_ordered = forms.DecimalField(required=True, label='Price')  
    comments_ordered = forms.CharField(required=False, label='Comments')

    def __init__(self, *args, **kwargs):
        super(NewPOItemForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('product', css_class='col-md-2'),
                Div('qty_approved', css_class='col-md-2'),
                Div('qty_ordered', css_class='quantity col-md-2'),
                Div('price_ordered', css_class='unit_price col-md-2'),
                Div('comments_ordered', css_class='col-md-4'),
                css_class='row',
            ),
        )
    
    # Ensure readonly/disabled 'product' field (Select/ChoiceField) is not editable by users 
    # More here: http://stackoverflow.com/questions/324477/in-a-django-form-how-do-i-make-a-field-readonly-or-disabled-so-that-it-cannot
    def clean_product(self):        
        if self.instance:
            return self.instance.product
        else: 
            return self.cleaned_data['product']

    def clean(self):
        cleaned_data = super(NewPOItemForm, self).clean()
        qty_ordered = self.cleaned_data['qty_ordered']
        qty_approved = self.cleaned_data['qty_approved']
        if qty_ordered > qty_approved:
            self.add_error('qty_ordered', 'Only '+str(qty_approved)+' items have been approved')
        return cleaned_data

    class Meta:
        model = OrderItem
        fields = ("product", "qty_approved", "qty_ordered", "price_ordered", "comments_ordered")


class ReceivePOItemForm(ModelForm):
    number = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), widget=forms.Select(attrs={'readonly':'true'}))
    qty_ordered = forms.IntegerField(widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Ordered')
    qty_delivered = forms.IntegerField(required=True, label='Delivered')
    qty_returned = forms.IntegerField(required=True, label='Returned')
    comments_delivered = forms.CharField(required=False, label='Comments')


    def __init__(self, *args, **kwargs):
        super(ReceivePOItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('number', css_class='col-md-1'),   
                Div('product', css_class='col-md-2'),
                Div('qty_ordered', css_class='col-md-2'),
                Div('qty_delivered', css_class='col-md-2'),
                Div('qty_returned', css_class='col-md-2'),
                Div('comments_delivered', css_class='col-md-3'),
                css_class='row',
            ),
        )  

    # Ensure readonly 'product' field is not editable by users 
    # More here: http://stackoverflow.com/questions/324477/in-a-django-form-how-do-i-make-a-field-readonly-or-disabled-so-that-it-cannot   
    def clean_product(self):
        if self.instance:
            return self.instance.product
        else: 
            return self.cleaned_data['product']
    
    def clean(self):
        cleaned_data = super(ReceivePOItemForm, self).clean()
        qty_ordered = self.cleaned_data['qty_ordered']
        qty_delivered = self.cleaned_data['qty_delivered']
        qty_returned = self.cleaned_data['qty_returned']
        if qty_delivered + qty_returned > qty_ordered:
            self.add_error('qty_delivered', 'Delivered+returned should be less than ordered')
            self.add_error('qty_returned', 'Delivered+returned should be less than ordered')
        return cleaned_data            

    class Meta:
        model = OrderItem
        fields = ('number', 'product', 'qty_ordered', 'qty_delivered', 'qty_returned', 'comments_delivered')
    
class DebitNoteItemForm(ModelForm):
    desc = forms.CharField(required=True, label='Description')

    def __init__(self, *args, **kwargs):
        super(DebitNoteItemForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('desc', css_class='item-product col-md-5'),
                Div('quantity', css_class='item-quantity col-md-2'),
                Div('unit_price', css_class='item-price col-md-2'),
                Div('subtotal', css_class='item-subtotal col-md-2'),
                HTML('<a class="delete col-md-1" href="#"><i class="fa fa-trash"></i></a>'),
                css_class='row',
            ),
        )

    def clean(self):
        cleaned_data = super(DebitNoteItemForm, self).clean()
        quantity = self.cleaned_data['quantity']
        unit_price = self.cleaned_data['unit_price']
        subtotal = self.cleaned_data['subtotal']
        # Check that either quantity & price OR subtotal are filled in
        if not (subtotal or (quantity and unit_price)):
            if not subtotal:
                self.add_error('subtotal', 'Subtotal or price/quantity can not be left blank')
            elif not quantity:
                self.add_error('quantity', 'Quantity field must be filled in')
            elif not unit_price:
                self.add_error('unit_price', 'Price field must be filled in')
        return cleaned_data 

    class Meta:
        model = DebitNoteItem
        fields = ("desc", "quantity", "unit_price", "subtotal")

# (unbilled_items)
class SpendAllocationForm(ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    account_code = forms.ModelChoiceField(queryset=AccountCode.objects.all())
    spend = forms.DecimalField(required=True, label='Allocate Spend')

    def __init__(self, *args, **kwargs):
        super(SpendAllocationForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('department', css_class='col-md-3'),
                Div('', css_class='col-md-1'),
                Div('account_code', css_class='col-md-2'),
                Div('', css_class='col-md-1'),
                Div('spend', css_class='col-md-2'),
                Div('', css_class='col-md-2'),
                HTML('<a class="unbilled_items delete col-md-1" href="#"><i class="fa fa-trash"></i></a>'),
                css_class='row',
            ),
        )

    def clean(self):
        cleaned_data = super(SpendAllocationForm, self).clean()
        department = self.cleaned_data['department']
        account_code = self.cleaned_data['account_code']    
        # Check that the account code belongs to the department
        if not Department.objects.filter(pk=department.id, account_codes=account_code).exists():
            self.add_error('account_code', 'Account code must match department')
        return cleaned_data            

    class Meta:
        model = SpendAllocation
        fields = ('department', 'account_code', 'spend')

class DrawdownItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), required=True)
    qty_requested = forms.IntegerField(required=True, min_value=1, label='Quantity')
    comments_requested = forms.CharField(required=False, label='Comments')

    def __init__(self, *args, **kwargs):
        super(DrawdownItemForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('product', css_class='col-md-4'),                
                Div('qty_requested', css_class='col-md-2'),
                Div('comments_requested', css_class='col-md-5'),
                HTML('<a class="delete col-md-1" href="#"><i class="fa fa-trash"></i></a>'),
                css_class='row',
            ),
        )

    class Meta:
        model = DrawdownItem
        fields = ("product", "qty_requested", "comments_requested")

class ApproveDDItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), widget=forms.Select(attrs={'readonly':'true'}))
    qty_requested = forms.IntegerField(widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Requested')
    qty_approved = forms.IntegerField(required=True, label='Approved')
    comments_requested = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Request Comments')
    comments_approved = forms.CharField(required=False, label='Approval Comments')


    def __init__(self, *args, **kwargs):
        super(ApproveDDItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div( 
                Div('product', css_class='col-md-2'),
                Div('qty_requested', css_class='col-md-2'),                
                Div('comments_requested', css_class='col-md-3'),
                Div('qty_approved', css_class='col-md-2'),
                Div('comments_approved', css_class='col-md-3'),
                css_class='row',
            ),
        )  

    # Ensure readonly 'product' field (Select/ChoiceField) is not editable by users 
    # More here: http://stackoverflow.com/questions/324477/in-a-django-form-how-do-i-make-a-field-readonly-or-disabled-so-that-it-cannot   
    def clean_product(self):
        if self.instance:
            return self.instance.product
        else: 
            return self.cleaned_data['product']

    def clean(self):
        cleaned_data = super(ApproveDDItemForm, self).clean()
        qty_approved = self.cleaned_data['qty_approved']
        qty_requested = self.cleaned_data['qty_requested']
        if qty_approved <= 0:
            self.add_error('qty_approved', 'Quantity must be greater than 0')
        elif qty_approved > qty_requested:
            self.add_error('qty_approved', 'Only '+str(qty_requested)+' items have been requested')
        return cleaned_data

    class Meta:
        model = DrawdownItem
        fields = ('product', 'qty_requested', 'qty_approved', 'comments_requested', 'comments_approved')

class CallDrawdownItemForm(ModelForm):
    number = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), widget=forms.Select(attrs={'readonly':'true'}))
    qty_approved = forms.IntegerField(widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Approved')
    qty_drawndown = forms.IntegerField(required=True, label='Drawndown')
    comments_drawdown = forms.CharField(required=False, label='Comments')


    def __init__(self, *args, **kwargs):
        super(CallDrawdownItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('number', css_class='col-md-2'),   
                Div('product', css_class='col-md-3'),
                Div('qty_approved', css_class='col-md-2'),
                Div('qty_drawndown', css_class='col-md-2'),
                Div('comments_drawdown', css_class='col-md-3'),
                css_class='row',
            ),
        )  

    # Ensure readonly 'product' field is not editable by users 
    # More here: http://stackoverflow.com/questions/324477/in-a-django-form-how-do-i-make-a-field-readonly-or-disabled-so-that-it-cannot   
    def clean_product(self):
        if self.instance:
            return self.instance.product
        else: 
            return self.cleaned_data['product']

    def clean(self):
        cleaned_data = super(CallDrawdownItemForm, self).clean()
        qty_drawndown = self.cleaned_data['qty_drawndown']
        qty_approved = self.cleaned_data['qty_approved']
        if qty_drawndown > qty_approved:
            self.add_error('qty_drawndown', 'Only '+str(qty_approved)+' items have been approved')
        return cleaned_data

    class Meta:
        model = DrawdownItem
        fields = ('number', 'product', 'qty_approved', 'qty_drawndown', 'comments_drawdown')



####################################
###       DOCUMENT FORMS         ### 
####################################

class RequisitionForm(ModelForm):
    date_due = forms.DateField(initial=timezone.now, required=True, widget=forms.TextInput(attrs={'type': 'date'}))
    # currency = forms.ChoiceField(settings.CURRENCIES, initial='USD')
    comments = forms.CharField(required=False, max_length=500, widget=forms.Textarea(attrs={'rows':3, 'cols':60}))
    department = forms.ModelChoiceField(queryset=Department.objects.none(), required=True)
    next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        super(RequisitionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(            
            Div(
                Div('number', css_class='col-md-3'),
                Div('department', css_class='col-md-3'),
                Div('date_due', css_class='col-md-3'),
                Div('next_approver', css_class='col-md-3'),
                css_class='row',
            ),
            Div(
                Div('comments', css_class='col-md-6'),
                css_class='row',
            )
        )    

    def clean(self):
        cleaned_data = super(RequisitionForm, self).clean()
        date_due = self.cleaned_data['date_due']
        if date_due < timezone.now().date():
            self.add_error('date_due', 'Date due must be in the future')
        return cleaned_data

    def save(self, commit=True):
        if self.clean():
            instance = super(RequisitionForm, self).save(commit=False)
            if commit:
                instance.save()
            return instance

    class Meta:
        model = Requisition
        fields = ("number", "date_due", "comments", "department", "next_approver")


class PurchaseOrderForm(ModelForm):
    date_due = forms.DateField(initial=timezone.now, required=True, widget=forms.TextInput(attrs={'type': 'date'} ))
    comments = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={'rows':5, 'cols':50}))
    cost_shipping = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, min_value=0)
    cost_other = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, min_value=0)
    # discount_percent = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    discount_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, min_value=0)
    # tax_percent = forms.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, min_value=0)
    terms = forms.CharField(max_length=5000, required=False, widget=forms.Textarea(attrs={'rows':5, 'cols':50}))
    vendor_co = forms.ModelChoiceField(queryset=VendorCo.objects.all())
    billing_add = forms.ModelChoiceField(queryset=Location.objects.all(), required=True, label="Billing Address")
    shipping_add = forms.ModelChoiceField(queryset=Location.objects.all(), required=True, label="Shipping Address")

    def __init__(self, *args, **kwargs):
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean(self):
        cleaned_data = super(PurchaseOrderForm, self).clean()
        date_due = self.cleaned_data['date_due']
        if date_due < timezone.now().date():
            self.add_error('date_due', 'Date due must be in the future')
        return cleaned_data

    class Meta:
        model = PurchaseOrder
        fields = ("number", "date_due", "vendor_co", "billing_add", "shipping_add", "comments", "terms", 
                 "tax_amount", "cost_shipping", "discount_amount", "cost_other")

class InvoiceForm(ModelForm):
    number = forms.CharField(required=True, label="Invoice Number")
    date_issued = forms.DateTimeField(initial=timezone.now, label="Date Issued", widget=forms.TextInput(attrs={'type': 'date'}))
    date_due = forms.DateTimeField(initial=timezone.now, label="Date Due", widget=forms.TextInput(attrs={'type': 'date'}))
    next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.all(), required=True)
    comments = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={'rows':5, 'cols':50}))

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean(self):
        cleaned_data = super(InvoiceForm, self).clean()
        date_due = self.cleaned_data['date_due']
        date_issued = self.cleaned_data['date_issued']
        if date_due < timezone.now().date():
            self.add_error('date_due', timezone.now().date())
            # 'Date due must be in the future'
        elif date_due < date_issued:
            self.add_error('date_due', 'Date due must be after issue date')
        return cleaned_data

    class Meta:
        model = Invoice
        fields = ("number", "date_issued", "date_due", "next_approver", "comments",
                 "tax_amount", "cost_shipping", "discount_amount", "cost_other",)
 

class DebitNoteForm(ModelForm):
    comments = forms.CharField(required=False, max_length=500, widget=forms.Textarea(attrs={'rows':3, 'cols':60}))
    vendor_co = forms.ModelChoiceField(label="Vendor", queryset=VendorCo.objects.none(), required=True)
    invoices = forms.ModelChoiceField(label="Invoice", queryset=Invoice.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        super(DebitNoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(            
            Div(
                Div('number', css_class='col-md-4'),
                Div('vendor_co', css_class='col-md-4'),
                Div('invoices', css_class='col-md-4'),
                css_class='row',
            ),
            Div(
                Div('comments', css_class='col-md-6'),
                css_class='row',
            )
        )

    def clean(self):
        cleaned_data = super(DebitNoteForm, self).clean()
        # If invoice's vendor != vendor_co selected
        invoice = self.cleaned_data['invoices']
        vendor_co = self.cleaned_data['vendor_co']
        if invoice.vendor_co != vendor_co:
            self.add_error('invoice', 'Please ensure the invoice vendor matches the vendor selected')

    class Meta:
        model = DebitNote
        fields = ("number", "vendor_co", "invoices", "comments",
            "tax_amount", "cost_shipping", "discount_amount", "cost_other")

class DrawdownForm(ModelForm): 
    date_due = forms.DateField(initial=timezone.now, required=True, widget=forms.TextInput(attrs={'type': 'date'}))
    comments = forms.CharField(required=False, max_length=500, widget=forms.Textarea(attrs={'rows':3, 'cols':60}))
    next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(DrawdownForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(            
            Div(
                Div('number', css_class='col-md-1'),
                Div('date_due', css_class='col-md-2'),
                Div('location', css_class='col-md-3'),
                Div('department', css_class='col-md-3'),                
                Div('next_approver', css_class='col-md-3'),
                css_class='row',
            ),
            Div(
                Div('comments', css_class='col-md-6'),
                css_class='row',
            )
        )    

    def clean(self):
        cleaned_data = super(DrawdownForm, self).clean()
        date_due = self.cleaned_data['date_due']
        if date_due < timezone.now().date():
            self.add_error('date_due', 'Date due must be in the future')
        return cleaned_data

    class Meta:
        model = Drawdown
        fields = ("number", "date_due", "comments", "location", "department", "next_approver")      

####################################
###         OTHER FORMS          ### 
####################################

class PriceAlertForm(ModelForm):
    commodity = forms.ModelChoiceField(Commodity.objects.all(), required=True)
    alert_price = forms.DecimalField(required=True, min_value=0, label='Alert Trigger Price')

    def __init__(self, *args, **kwargs):
        super(PriceAlertForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False   
        self.helper.layout = Layout(            
            Div(
                Div('commodity', css_class='commodity col-md-6'),
                Div('alert_price', css_class='col-md-6'),
                css_class='row',
            ),
        )  

    class Meta:
        model = PriceAlert
        fields = ("commodity", "alert_price",)

class FileForm(ModelForm):    
    file = forms.FileField(required=False)
    comments = forms.CharField(required=False, label='Notes', widget=forms.Textarea(attrs={'rows':3, 'cols':20}))

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False   
        self.helper.layout = Layout(            
            Div(
                Div('file', css_class='col-md-6'),
                Div('comments', css_class='col-md-6'),
                css_class='row',
            ),
        )     
    
    # To manage file upload size (http://stackoverflow.com/questions/2472422/django-file-upload-size-limit)
    def clean_content(self):
        content = self.cleaned_data['content']
        # Confirming file type - (image or text or application/pdf). Specific file extensions verified in validators.py
        content_type = content.content_type.split('/')[0] 
        if content_type in conf_settings.CONTENT_TYPES:
            if content._size > conf_settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        else:
            raise forms.ValidationError(_('File type is not supported'))
        return content

    class Meta:
        model = File
        fields = ("file", "comments", )

class UploadCSVForm(forms.Form):
    file = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super(UploadCSVForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False      


class ApprovalRoutingForm(forms.Form):
    approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.none(), required=True)
    approval_threshold = forms.DecimalField(required=True, label='Threshold Amount')

    def __init__(self, *args, **kwargs):
        super(ApprovalRoutingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('approver', css_class='col-md-6'),   
                Div('approval_threshold', css_class='col-md-6'),
                css_class='row',
            ),
        )

    def save(self):
        instance = super(ApprovalRoutingForm, self).save(commit=False)
        approver = self.cleaned_data['approver']
        approval_threshold = self.cleaned_data['approval_threshold']        
        approver.approval_threshold=approval_threshold
        approver.save()
        return approver
