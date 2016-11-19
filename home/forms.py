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
    name = forms.CharField(required=True)
    company = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    body = forms.CharField(required=False, widget = forms.Textarea(),)

    helper = FormHelper()
    helper.add_input(Submit('Submit', 'Submit', css_class="button button-small"))
    helper.layout = Layout(
        Field('topic', css_class='form-control'),
        Field('name', css_class='form-control'),
        Field('company', css_class='form-control'),
        Field('email', css_class='form-control'),
        Field('body', css_class='form-control', title="Comments"),
    )

    class Meta:
        model = ContactRequest
        fields = ('topic', 'name', 'company', 'email', 'body')





