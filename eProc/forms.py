from django import forms
from django.conf import settings
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
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True) 
    email = forms.EmailField(required=True)
    # profile_pic = forms.ImageField(label="Profile Picture", required=False)
    
    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helperReadOnly = FormHelper()
        self.helperReadOnly.layout = Layout(
            Field('username', css_class='form-control', readonly=True),
            Field('email', css_class='form-control', readonly=True),
        )
        self.helperReadOnly.form_tag = False

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

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

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

class ChangeUserForm(UserChangeForm):

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
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


# CREATING A USER WITH A TEMP PASSWORD
class AddUserForm(forms.Form):  
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True) 
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
            Div('email', css_class='col-md-12'),
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
            user.is_active=False
            user.save()
            return user


####################################
###        COMPANY FORMS         ### 
####################################

class BuyerProfileForm(ModelForm):  
    role = forms.ChoiceField(settings.ROLES, required=True, label="<i class='fa fa-user'></i> Role")
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label="<i class='fa fa-building'></i> Department")
    location = forms.ModelChoiceField(queryset=Location.objects.all(), label="<i class='fa fa-building'></i> Location")

    def __init__(self, *args, **kwargs):
        super(BuyerProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('location', css_class='col-md-6'),
                Div('department', css_class='col-md-6'),
                Div('role', css_class='col-md-12'),
                css_class='row',
            ),
        )

    class Meta:
        model = BuyerProfile
        fields = ("role", "department", "location")
        

class BuyerCoForm(forms.ModelForm):
    name = forms.CharField(required=True)
    currency = forms.ChoiceField(settings.CURRENCIES, required=True, )
    logo = forms.ImageField(required=False)

    helper = FormHelper()
    helper.layout = Layout(
        Field('name', css_class='form-control'),
        Field('currency', css_class='form-control'),
    )
    helper.form_tag = False

    class Meta:
        model = BuyerCo
        fields = ('name', 'currency')


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

class LocationForm(ModelForm):
    loc_type = forms.ChoiceField(settings.LOCATION_TYPES, label="<i class='fa fa-map-marker'></i> Address Type")
    address1 = forms.CharField(required=True, label="<i class='fa fa-home'></i> Address Line 1")
    address2 = forms.CharField(required=False, label="<i class='fa fa-home'></i> Address Line 2")
    city = forms.CharField(required=True, label="<i class='fa fa-location-arrow'></i> City")
    state = forms.CharField(required=True, label="<i class='fa fa-location-arrow'></i> State")
    zipcode = forms.CharField(required=True, label="<i class='fa fa-location-arrow'></i> Zip Code")
    country = forms.ChoiceField(settings.COUNTRIES, required=True, initial='India', label="<i class='fa fa-globe'></i> Country")
    phone = forms.CharField(required=False, label="<i class='fa fa-phone'></i> Phone Number")
    email = forms.EmailField(required=False, label="<i class='fa fa-envelope'></i> Email")
    
    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('loc_type', css_class='col-md-12'),
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
        fields = ('loc_type', 'address1', 'address2', 'city', 'state', 'country', 'zipcode', 'phone', 'email')        

####################################
###       SETTINGS FORMS         ### 
####################################

class DepartmentForm(ModelForm):
    name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = Department
        fields = ("name", )

class AccountCodeForm(ModelForm):
    expense_type = forms.ChoiceField(settings.EXPENSE_TYPES, required=True, )
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
###   PRODUCT & ITEM FORMS       ### 
####################################

class CatalogItemForm(ModelForm):
    name = forms.CharField(required=True)
    desc = forms.CharField()
    sku = forms.CharField(required=True)
    threshold = forms.IntegerField(label="Threshold quantity", help_text='Min. inventory level before alert is triggered.', required=False)
    unit_price = forms.DecimalField(required=True, min_value=0)
    unit_type = forms.CharField(required=True)
    # currency = forms.ChoiceField(settings.CURRENCIES, required=True, initial='USD')
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
                Div('threshold', css_class='col-md-8'),                
                css_class='row',
            ),                        
        )

    class Meta:
        model = CatalogItem
        fields = ('name', 'desc', 'sku', 'threshold', 'unit_price', 'unit_type', 'category', 'vendor_co')


class OrderItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), required=True)
    account_code = forms.ModelChoiceField(queryset=AccountCode.objects.all(), required=True)
    quantity = forms.IntegerField(required=True, min_value=1)
    comments = forms.CharField(required=False,)

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('product', css_class='col-md-3'),                
                Div('quantity', css_class='col-md-2'),
                Div('account_code', css_class='col-md-2'),
                Div('comments', css_class='col-md-4'),
                HTML('<div class="col-md-1 delete" style="margin-top: 2em;">' +
                        '<a href="#"><i class="fa fa-trash"></i></a>' +
                    '</div>'),
                css_class='row',
            ),
        )

    class Meta:
        model = OrderItem
        fields = ("product", "quantity", "account_code", "comments")

class DrawdownItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), required=True)
    quantity = forms.IntegerField(required=True, min_value=1)
    comments = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(DrawdownItemForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('product', css_class='col-md-4'),                
                Div('quantity', css_class='col-md-2'),
                Div('comments', css_class='col-md-4'),
                HTML('<a class="delete col-md-1" style="margin-top:30px" href="#"><i class="fa fa-trash"></i></a>'),
                css_class='row',
            ),
        )

    class Meta:
        model = OrderItem
        fields = ("product", "quantity", "comments")

####################################
###       DOCUMENT FORMS         ### 
####################################

class RequisitionForm(ModelForm):    
    number = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    date_due = forms.DateField(initial=timezone.now, required=True, widget=forms.TextInput(attrs={'type': 'date'}))
    # currency = forms.ChoiceField(settings.CURRENCIES, initial='USD')
    comments = forms.CharField(required=False, max_length=500, widget=forms.Textarea(attrs={'rows':3, 'cols':60}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.all(), required=True)

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

    class Meta:
        model = Requisition
        fields = ("number", "date_due", "comments", "department", "next_approver")


class PurchaseOrderForm(ModelForm):    
    number = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    date_due = forms.DateField(initial=timezone.now, required=True, widget=forms.TextInput(attrs={'type': 'date'} ))
    comments = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={'rows':5, 'cols':60}))
    next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.all(), required=False)

    cost_shipping = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, min_value=0)
    cost_other = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, min_value=0)
    # discount_percent = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    discount_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, min_value=0)
    # tax_percent = forms.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, min_value=0)
    terms = forms.CharField(max_length=5000, required=False, widget=forms.Textarea(attrs={'rows':5, 'cols':60}))
    vendor_co = forms.ModelChoiceField(queryset=VendorCo.objects.all())
    billing_add = forms.ModelChoiceField(queryset=Location.objects.all(), required=True, label="Billing Address")
    shipping_add = forms.ModelChoiceField(queryset=Location.objects.all(), required=True, label="Shipping Address")

    def __init__(self, *args, **kwargs):
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = PurchaseOrder
        fields = ("number", "date_due", "date_issued", "comments", "cost_shipping", "cost_other", "next_approver",
                  "discount_amount", "tax_amount", "terms", "vendor_co", "billing_add", "shipping_add")

class InvoiceForm(ModelForm):
    number = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}), label="Invoice Number")
    date_issued = forms.DateTimeField(initial=timezone.now, label="Invoice Date", widget=forms.TextInput(attrs={'type': 'date'}))
    date_due = forms.DateTimeField(initial=timezone.now, label="Date Due", widget=forms.TextInput(attrs={'type': 'date'}))
    vendor_co = forms.ModelChoiceField(queryset=VendorCo.objects.all(), label="Vendor")    

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(            
            Div(
                Div('number', css_class='col-md-6'),
                Div('date_issued', css_class='col-md-3'),
                Div('date_due', css_class='col-md-3'),                                
                css_class='row',
            ),
            Div(
                Div('vendor_co', css_class='col-md-5', css_id='vendor_co'),
                HTML('<div class="col-md-1" style="margin-top:28px;">'+
                        '<button type="button" id="selectVendor" class="label label-warning">Select</button>' +
                     '</div>'
                ),
                Div('purchase_order', css_class='col-md-5', css_id="po_list"),
                HTML('<div class="col-md-1" style="margin-top:28px;">'+
                        '<button type="button" id="selectPO" class="label label-warning">Select</button>' +
                     '</div>'
                ),
                css_class='row'
            ),
            Div(
                Div('comments', css_class='col-md-6'),
                css_class='row',
            )
        ) 

    # Add basic form validation to clean method
    def clean(self):
        cleaned_data = super(InvoiceForm, self).clean()
        date_due = self.cleaned_data['date_due']
        date_issued = self.cleaned_data['date_issued']
        if date_issued > date_due:
            raise forms.ValidationError('Date due must be after issue date')
        # TODO: Add more checks
        # TODO: Make {{form.errors}} show in {{messages}}
    
    # Override save to make datetime objects timezone aware    
    def save(self, commit=True):
        instance = super(InvoiceForm, self).save(commit=False)
        # instance.date_due = timezone.make_aware(self.cleaned_data['date_due'], timezone.now())
        # instance.date_issued = timezone.make_aware(self.cleaned_data['date_issued'], timezone.now())
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Invoice
        fields = ("number", "date_issued", "date_due", "comments", "purchase_order", "vendor_co")
 

class DrawdownForm(ModelForm):       
    number = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    date_due = forms.DateField(initial=timezone.now, required=True, widget=forms.TextInput(attrs={'type': 'date'}))
    comments = forms.CharField(required=False, max_length=500, widget=forms.Textarea(attrs={'rows':3, 'cols':60}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(DrawdownForm, self).__init__(*args, **kwargs)
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

    class Meta:
        model = Drawdown
        fields = ("number", "date_due", "comments", "department", "next_approver")      

####################################
###         OTHER FORMS          ### 
####################################

class FileForm(ModelForm):    
    file = forms.FileField(required=True, label="Upload Invoice from Vendor")
    comments = forms.CharField(required=False, label='Invoice notes', widget=forms.Textarea(attrs={'rows':3, 'cols':20}))

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False        

    class Meta:
        model = File
        fields = ("file", "comments", )

class UploadCSVForm(forms.Form):
    file = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super(UploadCSVForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False      

class ReceivePOForm(ModelForm):
    number = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all(), widget=forms.TextInput(attrs={'readonly':'readonly'}))
    quantity = forms.IntegerField(widget=forms.TextInput(attrs={'readonly':'readonly'}), label='Requested')
    qty_delivered = forms.IntegerField(required=True, label='Delivered')
    qty_returned = forms.IntegerField(required=True, label='Returned')
    comments_delivery = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':2, 'cols':50}), label='Comments')


    def __init__(self, *args, **kwargs):
        super(ReceivePOForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('number', css_class='col-md-1'),   
                Div('product', css_class='col-md-2'),
                Div('quantity', css_class='col-md-2'),
                Div('qty_delivered', css_class='col-md-2'),
                Div('qty_returned', css_class='col-md-2'),
                Div('comments_delivery', css_class='col-md-3'),
                css_class='row',
            ),
        )

    class Meta:
        model = OrderItem
        fields = ('number', 'product', 'quantity', 'qty_delivered', 'qty_returned', 'comments_delivery')

class ApprovalRoutingForm(forms.Form):
    qty_delivered = forms.IntegerField(required=True)
    qty_returned = forms.IntegerField(required=True)
    comments_delivery = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':2, 'cols':50}))


    def __init__(self, *args, **kwargs):
        super(ApprovalRoutingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
