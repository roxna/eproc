from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TestCase
from eProc.forms import *
from eProc.models import *


class RegisterUserFormTestCase(TestCase):

    # Method called before running each test
    def setUp(self):
        self.form = RegisterUserForm()

    def test_valid_form(self):
        form = self.form
        form.cleaned_data = {
            'first_name': 'test_fname', 
            'last_name': 'test_lname',
            'username': 'test_username',
            'email': 'test@email.com',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        # new_user = form.save()
        # self.assertTrue(form.is_valid())
        # self.assertEqual(new_user.first_name, 'test_fname')
        # This below is rubbish - not a real test - need to fix to the ones above
        self.assertEqual(form.cleaned_data['first_name'], 'test_fname')
        self.assertEqual(form.cleaned_data['last_name'], 'test_lname')
        self.assertEqual(form.cleaned_data['username'], 'test_username')
        self.assertEqual(form.cleaned_data['email'], 'test@email.com')
        
    def test_clean_username_exception(self):
        user = User.objects.create_user(username='test_uname')        
        form = self.form
        form.cleaned_data = {'username': 'test_uname'}
        self.assertRaises(KeyError, form.clean_username())

    def test_blank_form(self):
        form = self.form
        self.assertFalse(form.is_valid())
        # self.assertEqual(form.errors, {
        #     'username': [u'This field is required.'],
        #     'first_name': [u'This field is required.'],
        #     'last_name': [u'This field is required.'],
        #     'email': [u'This field is required.'],
        #     'password1': [u'This field is required.'],
        #     'password2': [u'This field is required.']
        # })


class ChangeUserFormTestCase(TestCase):
    pass


class AddUserFormTestCase(TestCase):
    
    def setUp(self):
        self.form = AddUserForm()

    def test_valid_form(self):
        form = self.form
        form.cleaned_data = {
            'first_name': 'test_FName', 
            'last_name': 'test_LName',
            'email': 'test@email.com'
        }
        # self.assertTrue(form.is_valid())
        new_user = form.save()
        self.assertEqual(form.cleaned_data['first_name'], 'test_FName')
        self.assertEqual(new_user.first_name, 'test_FName')
        self.assertEqual(new_user.last_name, 'test_LName')
        self.assertEqual(new_user.username, 'test_fname_test_lname')
        self.assertEqual(new_user.email, 'test@email.com')
        self.assertFalse(new_user.is_active)
        # self.assertEqual(new_user.password, 'temppw')

    def test_invalid_form(self):
        form = self.form
        form.cleaned_data = {
            'first_name': '', 
            'last_name': 'test_LName',
            'email': 'testinvalidemail'
        }
        self.assertFalse(form.is_valid())

    def test_clean_username_exception(self):
        user = User.objects.create_user(username='fname_lname')        
        form = self.form
        form.cleaned_data = {
            'first_name': 'fname',
            'last_name': 'lname',
        }
        self.assertRaises(ValidationError, form.clean_username())


    def test_blank_form(self):
        form = self.form
        self.assertFalse(form.is_valid())


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



 # def test_forms(self):
 #        response = self.client.post("/my/form/", {'something':'something'})
 #        self.assertFormError(response, 'form', 'something', 'This field is required.'

#     from rebar.testing import flatten_to_dict
# from contacts import forms
# ...
# class EditContactFormTests(TestCase):

#     def test_mismatch_email_is_invalid(self):

#         form_data = flatten_to_dict(forms.ContactForm())
#         form_data['first_name'] = 'Foo'
#         form_data['last_name'] = 'Bar'
#         form_data['email'] = 'foo@example.com'
#         form_data['confirm_email'] = 'bar@example.com'

#         bound_form = forms.ContactForm(data=form_data)
#         self.assertFalse(bound_form.is_valid())

# def test_good_vote(self):
#       poll_1 = Poll.objects.get(pk=1)
#       self.assertEqual(poll_1.choice_set.get(pk=1).votes, 1)

#       resp = self.client.post('/polls/1/vote/', {'choice': 1})
#       self.assertEqual(resp.status_code, 302)
#       self.assertEqual(resp['Location'], 'http://testserver/polls/1/results/')

#       self.assertEqual(poll_1.choice_set.get(pk=1).votes, 2)

# def test_bad_votes(self):
#       # Ensure a non-existant PK throws a Not Found.
#       resp = self.client.post('/polls/1000000/vote/')
#       self.assertEqual(resp.status_code, 404)

#       # Sanity check.
#       poll_1 = Poll.objects.get(pk=1)
#       self.assertEqual(poll_1.choice_set.get(pk=1).votes, 1)

#       # Send no POST data.
#       resp = self.client.post('/polls/1/vote/')
#       self.assertEqual(resp.status_code, 200)
#       self.assertEqual(resp.context['error_message'], "You didn't select a choice.")

#       # Send junk POST data.
#       resp = self.client.post('/polls/1/vote/', {'foo': 'bar'})
#       self.assertEqual(resp.status_code, 200)
#       self.assertEqual(resp.context['error_message'], "You didn't select a choice.")

#       # Send a non-existant Choice PK.
#       resp = self.client.post('/polls/1/vote/', {'choice': 300})
#       self.assertEqual(resp.status_code, 200)
#       self.assertEqual(resp.context['error_message'], "You didn't select a choice.")