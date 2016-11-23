from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.db.models import Count
from django.forms import ModelForm
from eProc.models import *
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML

class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True) 
    email = forms.EmailField(required=True)
    # profile_pic = forms.ImageField(label="Profile Picture", required=False)
    
    helper = FormHelper()
    helper.form_tag = False

    helperReadOnly = FormHelper()
    helperReadOnly.layout = Layout(
        Field('username', css_class='form-control', readonly=True),
        Field('email', css_class='form-control', readonly=True),
    )
    helperReadOnly.form_tag = False

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

class ChangeUserForm(UserChangeForm):

    helper = FormHelper()
    helper.layout = Layout(
        Field('username', css_class='form-control', readonly=True),
        Field('email', css_class='form-control', readonly=True),
    )
    helper.form_tag = False

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')



# CREATING A USER WITH A TEMP PASSWORD
class AddUserForm(forms.Form):  
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True) 
    email = forms.EmailField(required=True)  
    
    helper = FormHelper()
    helper.form_tag = False

    def get_username(self):
        return self.cleaned_data['first_name']+self.cleaned_data['last_name']

    def clean_username(self):
        try:
            User.objects.get(username=self.get_username())
        except User.DoesNotExist :
            return self.get_username()
        raise forms.ValidationError("Duplicate username")

    def save(self):
        user = User.objects.create_user(username=self.clean_username(),
                                        email=self.cleaned_data['email'],
                                        password='temppw',
                                        )
        user.first_name=self.cleaned_data['first_name']
        user.last_name=self.cleaned_data['last_name']
        user.is_active=False
        user.save()
        return user

class BuyerProfileForm(ModelForm):  
    role = forms.ChoiceField(settings.ROLES, required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all())

    helper = FormHelper()
    helper.form_tag = False

    helperReadOnly = FormHelper()
    helperReadOnly.layout = Layout(
        Field('role', css_class='form-control', readonly=True),
        Field('department', css_class='form-control', readonly=True),
    )
    helperReadOnly.form_tag = False

    class Meta:
        model = BuyerProfile
        fields = ("role", "department")
        

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

class LoginForm(AuthenticationForm):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)

    helper = FormHelper()
    helper.form_tag = False


class DepartmentForm(ModelForm):
    name = forms.CharField(required=True)

    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = Department
        fields = ("name", )


class CatalogItemForm(ModelForm):
    name = forms.CharField(required=True)
    desc = forms.CharField()
    sku = forms.CharField(required=True)
    unit_price = forms.DecimalField(required=True)
    unit_type = forms.CharField(required=True)
    # currency = forms.ChoiceField(settings.CURRENCIES, required=True, initial='USD')
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    vendorCo = forms.ModelChoiceField(queryset=VendorCo.objects.all())

    helper = FormHelper() 
    helper.form_tag = False

    class Meta:
        model = CatalogItem
        fields = ('name', 'desc', 'sku', 'unit_price', 'unit_type', 'category', 'vendorCo')

class VendorCoForm(ModelForm):
    name = forms.CharField(required=True, label="Vendor Name")
    contact_rep = forms.CharField(required=False, label="Contact Rep")
    website = forms.URLField(required=False)

    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = VendorCo
        fields = ("name", "contact_rep", "website", "vendorID", "comments")

class CategoryForm(ModelForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = Category
        fields = ("name", "code")

class LocationForm(ModelForm):
    loc_type = forms.ChoiceField(settings.LOCATION_TYPES, label="Address Type")
    address1 = forms.CharField(required=True, label="Address Line 1")
    address2 = forms.CharField(required=False, label="Address Line 2")
    city = forms.CharField(required=True)
    state = forms.CharField(required=True)
    zipcode = forms.CharField(required=True)
    country = forms.ChoiceField(settings.COUNTRIES, required=True, initial='India')
    email = forms.EmailField(required=False)
    
    helper = FormHelper()    
    helper.form_tag = False

    class Meta:
        model = Location
        fields = ('loc_type', 'address1', 'address2', 'city', 'state', 'country', 'zipcode', 'phone', 'fax', 'email')        

class RequisitionForm(ModelForm):    
    number = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    date_due = forms.DateField(initial=timezone.now, required=True)
    # currency = forms.ChoiceField(settings.CURRENCIES, initial='USD')
    comments = forms.CharField(required=False, max_length=200, help_text="Any comments for approving/purchasing dept: ")
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.all())

    helper = FormHelper()
    helper.form_tag = False

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

    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = PurchaseOrder
        fields = ("number", "date_due", "comments", "cost_shipping", "cost_other", 
                  "discount_amount", "tax_amount", "terms", "vendorCo", "billing_add", "shipping_add")

class OrderItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all())
    account_code = forms.ModelChoiceField(queryset=AccountCode.objects.all())
    quantity = forms.IntegerField()
    comments = forms.CharField(required=False, help_text="Additional comments")

    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = OrderItem
        fields = ("product", "account_code", "quantity", "comments")
        

class UploadCSVForm(forms.Form):
    file = forms.FileField(required=True)

    helper = FormHelper()
    helper.form_tag = False


