from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Count
from django.forms import ModelForm
from eProc.models import *
from django.utils import timezone
# from crispy_forms.helper import FormHelper, FormSetHelper
# from crispy_forms.layout import Submit


class NewUserForm(UserCreationForm):
    ROLES = (
        (1, 'SuperUser'),
        (2, 'Requester'),
        (3, 'Approver'),
        (4, 'Purchaser'),
        (5, 'Receiver'),
        (6, 'Payer'),
    )
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)    
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(ROLES, required=True)
    department = forms.CharField()
    # department = forms.ModelChoiceField(Department)
    profile_pic = forms.ImageField(label="Profile Picture", required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "role", "department", "password1", "password2", "profile_pic")

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
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Username','class': 'form-control'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password','class': 'form-control'}))


class DepartmentForm(ModelForm):
    name = forms.CharField(required=True)

    class Meta:
        model = Department
        fields = ("name", )

class RequisitionForm(ModelForm):    
    # req_count = Requisition.objects.filter(buyerCo=user.buyer_profile.company).count()
    req_count = Requisition.objects.count()+1
    number = forms.CharField(initial="RO"+str(req_count))
    date_created = forms.DateTimeField(initial=timezone.now, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    date_due = forms.DateField(initial=timezone.now, required=True)
    CURRENCY_LIST = [('USD', 'USD'), ('INR', 'INR')]
    currency = forms.ChoiceField(CURRENCY_LIST, initial='USD')
    comments = forms.CharField(required=False, max_length=200, help_text="Any comments for approving/purchasing dept: ")  
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.all())
    # TO DOOOOOOOO FILTER FOR DEPT AND NEXT_APPROVER IN THE USER'S CO ONLY
    # department = forms.ModelChoiceField(queryset=Department.objects.filter(company=user.buyerCo))
    # next_approver = forms.ModelChoiceField(queryset=BuyerProfile.objects.filter(company=user.buyerCo).order_by('name'))

    class Meta:
        model = Requisition
        fields = ("number", "date_created", "date_due", "currency", "comments", "department", "next_approver")


class OrderItemForm(ModelForm):
    product = forms.ModelChoiceField(queryset=CatalogItem.objects.all())
    unit_price = forms.IntegerField()
    account_code = forms.ModelChoiceField(queryset=AccountCode.objects.all())
    quantity = forms.IntegerField()
    comments = forms.CharField(help_text="Additional comments")

    class Meta:
        model = OrderItem
        fields = ("product", "account_code", "quantity", "comments")

    # helper = FormSetHelper()
    # helper.add_input(Submit('Submit', 'Submit', css_class="btn-success")) 

