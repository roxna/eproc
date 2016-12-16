from django import forms
from django.forms import ModelForm, Textarea
from home.models import *
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Field, HTML

class ContactRequestForm(ModelForm):
    TOPICS = (
        ('Demo', 'I want to book a demo'),
        ('Pricing', 'I have a question about pricing'),
        ('Billing', 'I have a question about billing'),
        ('Partnerships', 'I want to talk about partnerships'),
        ('Other', 'Other'),
    )
    topic = forms.ChoiceField(TOPICS, required=True)
    body = forms.CharField(required=False, widget = forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(ContactRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('topic', css_class='form-control col-md-12'),
            HTML('<br></br>'),
            Field('body', css_class='form-control col-md-12',),
        )

    class Meta:
        model = ContactRequest
        fields = ('topic', 'body')


class AuthorForm(ModelForm):
    name = forms.CharField(max_length=40, required=True)
    company = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=254)

    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('name', css_class='form-control col-md-12 width-100'),
            HTML('<br></br>'),
            Field('company', css_class='form-control col-md-12 width-100',),
            HTML('<br></br>'),
            Field('email', css_class='form-control col-md-12 width-100',),
            HTML('<br></br>'),
        )

    class Meta:
        model = Author
        fields = ('name', 'company', 'email')

# class NewsletterForm(ModelForm):
#     email = forms.EmailField(max_length=254)

#     def __init__(self, *args, **kwargs):
#         super(NewsletterForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_tag = False

#     class Meta:
#         model = Author
#         fields = ('email',)
