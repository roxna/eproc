from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TestCase
from eProc.forms import *
from eProc.models import *

# https://github.com/kennethlove/Getting-Started-With-Django/blob/master/blog/tests/test_views.py

# class ViewTestCase(TestCase):
#     def create_user(self):
#         self.username = 'username'
#         self.password = 'password'
#         self.user = User.objects.create_user(username=self.username, email='test@test.com', password=self.password)

#     def test_register_page(self):
#         data = {
#             'username': self.username,
#             'email': 'test@test.com',
#             'password1': 'test',
#             'password2': 'test'
#         }
#         response = self.client.post(reverse('register'), data)

#         # Check this user was created in the database
#         self.assertTrue(User.objects.filter(username=self.username).exists())

#         # Check it's a redirect to the dashboard page
#         self.assertIsInstance(response, HttpResponseRedirect)
#         self.assertTrue(response.get('location').endswith(reverse('dashboard')))

#     def test_login_page(self):
#         data = {
#             'username': self.username,
#             'password': self.password
#         }
#         response = self.client.post(reverse('login'), data)

#         # Check it's a redirect to the dashboard page
#         self.assertIsInstance(response, HttpResponseRedirect)
#         self.assertTrue(response.get('location').endswith(reverse('dashboard')))
 
 # def test_whatever_list_view(self):
 #        w = self.create_whatever()
 #        url = reverse("whatever.views.whatever")
 #        resp = self.client.get(url)

 #        self.assertEqual(resp.status_code, 200)
 #        self.assertIn(w.title, resp.content)