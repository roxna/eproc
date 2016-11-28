from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TestCase
from eProc.forms import *
from eProc.models import *

class FormTestCase(TestCase):
    def test_clean_username(self):
        form = RegisterUserForm()
        form.cleaned_data = {
            'first_name': 'test_fname', 
            'last_name': 'test_lname',
            'username': 'test_username',
            'email': 'test@email.com'
        }
        self.assertEqual(form.cleaned_data['first_name'], 'test_fname')
        self.assertEqual(form.cleaned_data['last_name'], 'test_lname')
        self.assertEqual(form.cleaned_data['username'], 'test_username')
        self.assertEqual(form.cleaned_data['email'], 'test@email.com')

    def test_clean_username_exception(self):
        User.objects.create_user(username='test-user')
        form = RegisterUserForm()
        form.cleaned_data = {'username': 'test-user'}
        # Use a context manager to watch for the validation error being raised
        with self.assertRaises(ValidationError):
            form.clean_username()

    # def test_valid_form(self):
    #     w = Whatever.objects.create(title='Foo', body='Bar')
    #     data = {'title': w.title, 'body': w.body,}
    #     form = WhateverForm(data=data)
    #     self.assertTrue(form.is_valid())

    # def test_invalid_form(self):
    #     w = Whatever.objects.create(title='Foo', body='')
    #     data = {'title': w.title, 'body': w.body,}
    #     form = WhateverForm(data=data)
    #     self.assertFalse(form.is_valid())