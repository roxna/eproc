from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Count
from django.forms import ModelForm
from eProc.models import *
from django.utils import timezone

ROLES = ((1, 'SuperUser'),(2, 'Requester'),(3, 'Approver'),(4, 'Purchaser'),(5, 'Receiver'),(6, 'Payer'))  
CURRENCIES = (('USD', 'USD'),('INR', 'INR'))  

class UserForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True) 
    username = forms.CharField(required=True)    
    email = forms.EmailField(required=True)
    # profile_pic = forms.ImageField(label="Profile Picture", required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")

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

class BuyerProfileForm(ModelForm):  
    role = forms.ChoiceField(ROLES, required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all())

    # READONLY_FIELDS = ('role', 'department')

    class Meta:
        model = BuyerProfile
        fields = ("role", "department")    

    # def __init__(self, read_only=False, *args, **kwargs):
    #     super(BuyerProfileForm, self).__init__(*args, **kwargs)
    #     if read_only:
    #         for field in self.READONLY_FIELDS:
    #             self.fields[field].widget.attrs['readonly'] = True
        

class CompanyProfileForm(forms.ModelForm):
    name = forms.CharField(required=True)
    currency = forms.ChoiceField(CURRENCIES, required=True)
    logo = forms.ImageField()

    class Meta:
        model = BuyerCo
        fields = ('name', 'currency', 'logo')

class LoginForm(AuthenticationForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Username','class': 'form-control'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password','class': 'form-control'}))


class DepartmentForm(ModelForm):
    name = forms.CharField(required=True)

    class Meta:
        model = Department
        fields = ("name", )


class CatalogItemForm(ModelForm):
    name = forms.CharField(required=True)
    desc = forms.CharField()
    sku = forms.CharField(required=True)
    unit_price = forms.DecimalField(required=True)
    unit_type = forms.CharField(required=True)
    currency = forms.ChoiceField(CURRENCIES, required=True, initial='USD')
    # Category, VendorCo queryset SPECIFIC to BuyerCo updated in views.py
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    vendorCo = forms.ModelChoiceField(queryset=VendorCo.objects.all())

    class Meta:
        model = CatalogItem
        fields = ('name', 'desc', 'sku', 'unit_price', 'unit_type', 'currency', 'category', 'vendorCo')

class VendorForm(ModelForm):
    name = forms.CharField(required=True)

    class Meta:
        model = VendorCo
        fields = ("name", )

class LocationForm(ModelForm):
    name = forms.CharField()
    address1 = forms.CharField()
    address2 = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()
    zipcode = forms.IntegerField()
    country = forms.CharField()
    phone = forms.IntegerField(required=False)
    email = forms.CharField(required=False)
    
    class Meta:
        model = Location
        fields = ('name', 'address1', 'address2', 'city', 'state', 'country', 'zipcode', 'phone', 'email')        

class VendorProfileForm(ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = VendorCo
        fields = ('first_name', 'last_name', 'email')

class RequisitionForm(ModelForm):    
    number = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    date_due = forms.DateField(initial=timezone.now, required=True)
    # currency = forms.ChoiceField(CURRENCIES, initial='USD')
    comments = forms.CharField(required=False, max_length=200, help_text="Any comments for approving/purchasing dept: ")
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.all())

    class Meta:
        model = Requisition
        fields = ("number", "date_due", "comments", "department", "next_approver")


class PurchaseOrderForm(ModelForm):    
    number = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    date_due = forms.DateField(initial=timezone.now, required=True)
    comments = forms.CharField(required=False, max_length=500, help_text="PO Notes")
    # next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.all(), required=False)

    cost_shipping = forms.DecimalField(max_digits=10, decimal_places=2, initial=0)
    cost_other = forms.DecimalField(max_digits=10, decimal_places=2, initial=0)
    # discount_percent = forms.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0)
    # tax_percent = forms.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, widget=forms.NumberInput(attrs={ "placeholder": 0}))
    terms = forms.CharField(max_length=5000)
    vendorCo = forms.ModelChoiceField(queryset=VendorCo.objects.all()) #Update queryset in views.py
    billing_add = forms.ModelChoiceField(queryset=Location.objects.all()) #Update queryset in views.py
    shipping_add = forms.ModelChoiceField(queryset=Location.objects.all()) #Update queryset in views.py

    class Meta:
        model = PurchaseOrder
        fields = ("number", "date_due", "comments", "cost_shipping", "cost_other", 
                  "discount_amount", "tax_amount", "terms", "vendorCo", "billing_add", "shipping_add")

class OrderItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all())
    account_code = forms.ModelChoiceField(queryset=AccountCode.objects.all())
    quantity = forms.IntegerField()
    comments = forms.CharField(required=False, help_text="Additional comments")

    class Meta:
        model = OrderItem
        fields = ("product", "account_code", "quantity", "comments")
        

class UploadCSVForm(forms.Form):
    file = forms.FileField(required=True)


