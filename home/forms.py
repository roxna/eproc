from django import forms
from django.forms import ModelForm, Textarea
from home.models import *
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML

class ContactRequestForm(ModelForm):
    TOPICS = (
        ('Demo', 'I want to book a demo'),
        ('Pricing', 'I have a question about pricing'),
        ('Billing', 'I have a question about billing'),
        ('Partnerships', 'I want to talk about partnerships'),
        ('Other', 'Other'),
    )
    topic = forms.ChoiceField(TOPICS, required=True)
    # name = forms.CharField(required=True)
    # company = forms.CharField(required=True)
    # email = forms.EmailField(required=True)
    body = forms.CharField(required=False, widget = forms.Textarea())

    helper = FormHelper()
    # helper.add_input(Submit('Submit', 'Submit', css_class="button button-small"))
    helper.layout = Layout(
        Field('topic', css_class='form-control'),
        # Field('name', css_class='form-control'),
        # Field('company', css_class='form-control'),
        # Field('email', css_class='form-control'),
        Field('body', css_class='form-control', title="Comments"),
    )
    helper.form_tag = False

    class Meta:
        model = ContactRequest
        fields = ('topic', 'body')


class AuthorForm(ModelForm):
    name = forms.CharField(max_length=40, required=True)
    title = forms.CharField(max_length=40, required=False)
    company = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=254)

    helper = FormHelper()
    helper.layout = Layout(
        Field('name', css_class='form-control'),
        # Field('title', css_class='form-control', required=True),
        Field('company', css_class='form-control', required=True),
        Field('email', css_class='form-control', required=True),
    )
    helper.form_tag = False

    class Meta:
        model = Author
        fields = ('name', 'company', 'email')

