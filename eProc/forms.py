from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
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
    helper.layout = Layout(
        Field('username', css_class='form-control'),
        Field('first_name', css_class='form-control'),
        Field('last_name', css_class='form-control'),
        Field('email', css_class='form-control'),
        Field('password1', css_class='form-control'),
        Field('password2', css_class='form-control'),
    )    
    helper.form_tag = False

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
    helper.layout = Layout(
        Field('role', css_class='form-control'),
        Field('department', css_class='form-control'),
    )
    helper.form_tag = False

    # READONLY_FIELDS = ('role', 'department')

    class Meta:
        model = BuyerProfile
        fields = ("role", "department")    

    # def __init__(self, read_only=False, *args, **kwargs):
    #     super(BuyerProfileForm, self).__init__(*args, **kwargs)
    #     if read_only:
    #         for field in self.READONLY_FIELDS:
    #             self.fields[field].widget.attrs['readonly'] = True
        

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
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Username','class': 'form-control'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password','class': 'form-control'}))

    helper = FormHelper()
    helper.layout = Layout(
        Field('username', css_class='form-control'),
        Field('password', css_class='form-control'),
    )
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

class VendorForm(ModelForm):
    name = forms.CharField(required=True)

    helper = FormHelper()
    helper.layout = Layout(
        Field('name', css_class='form-control', placeholder='Vendor Name'),
    )
    helper.form_tag = False

    class Meta:
        model = VendorCo
        fields = ("name", )

class CategoryForm(ModelForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = Category
        fields = ("name", "code")

class LocationForm(ModelForm):
    # name = forms.CharField()
    typee = forms.ChoiceField(settings.LOCATION_TYPES)
    # address1 = forms.CharField(required=False)
    # address2 = forms.CharField()
    # city = forms.CharField()
    # state = forms.CharField()
    # zipcode = forms.IntegerField()
    country = forms.ChoiceField(settings.COUNTRIES, required=True, initial='India')
    # phone = forms.IntegerField(required=False)
    # email = forms.CharField(required=False)
    
    helper = FormHelper()    
    helper.layout = Layout(
        Field('typee', css_class='form-control'),
        Field('address1', css_class='form-control', placeholder='Address Line 1'),
        Field('address2', css_class='form-control', placeholder='Address Line 2'),
        Field('city', css_class='form-control'),
        Field('zipcode', css_class='form-control'),
        Field('state', css_class='form-control'),
        Field('country', css_class='form-control'),
        Field('phone', css_class='form-control'),
        Field('email', css_class='form-control'),
    )
    # helper.all().wrap(Field, css_class="col-md-6") #TODO: WRAP FIELDS IN col-md-6 divs
    helper.form_tag = False

    class Meta:
        model = Location
        fields = ('address1', 'typee', 'address2', 'city', 'state', 'country', 'zipcode', 'phone', 'email')        

class VendorProfileForm(ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = VendorCo
        fields = ('first_name', 'last_name', 'email')

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


