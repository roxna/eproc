from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, TestCase
from eProc.forms import *
from eProc.models import *

# https://github.com/kennethlove/Getting-Started-With-Django/blob/master/blog/tests/test_views.py


class ViewTestCase(TestCase):

####################################
###         TEST SET UP         ### 
####################################

    def setUp(self):
        self.username = 'test_views_username'
        self.first_name = 'test_views_fname'
        self.last_name = 'test_views_lname'
        self.password = 'test_views_password'
        self.email = 'test_views@email.com'

        self.buyer_co_name = 'Test Buyer Co'
        self.buyer_co_currency = 'USD'
        self.client = Client()

        self.data = {
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password1': self.password,
            'password2': self.password,
            'name': self.buyer_co_name,
            'currency': self.buyer_co_currency,
        }  

    def create_user(self, is_active=False):        
        return User.objects.create_user(username=self.username, email=self.email, password=self.password, is_active=is_active)

    # def create_buyerCo(self):
    #     return BuyerCo.objects.create()
    
    def log_user_in(self):
        self.client.login(username=self.username, password=self.password)

####################################
###         SETTINGS         ### 
####################################

    def test_get_departments(self):
        pass


####################################
###         REGISTRATION         ### 
####################################

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_page_submits_valid_data(self):
        data = self.data 
        response = self.client.post(reverse('register'), data)

        # Check this user, buyerCo, dept, buyerProfile were created in the database
        user = User.objects.filter(username=self.username)
        buyer_co = BuyerCo.objects.filter(name=self.buyer_co_name, currency=self.buyer_co_currency)
        company = Company.objects.filter(name=self.buyer_co_name, currency=self.buyer_co_currency)
        self.assertTrue(user.exists())
        # self.assertFalse(user.is_active)  #ERROR: AttributeError: 'QuerySet' object has no attribute 'is_active'
        self.assertTrue(buyer_co.exists())
        self.assertTrue(company.exists())
        self.assertTrue(BuyerProfile.objects.filter(user=user, company=company).exists())
        self.assertTrue(Department.objects.filter(name='Admin').exists())

        # Check activation email is sent out

        # Check it's a redirect (302 Redirect) to the thankyou page        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.get('location').endswith(reverse('thankyou')))
        self.assertIsInstance(response, HttpResponseRedirect)

    # TODO: NOT WORKING
    def test_register_page_invalid_username(self):
        data = self.data
        data['username'] = ''
        response = self.client.post(reverse('register'), data)
        # self.assertFormError(response, 'form', 'username', 'This field is required.')
    
    # TODO: NOT WORKING
    def test_register_page_invalid_email(self):
        data = self.data
        data['email'] = 'testinvalidemailaddress'
        response = self.client.post(reverse('register'), data)
        # self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')

    # TODO: NOT WORKING
    def test_register_page_blank_data(self):
        data = {}
        response = self.client.post(reverse('register'), data)          
        # self.assertFormError(response, 'form', 'username', 'This field is required.')
        # self.assertFormError(response, 'form', 'password1', 'This field is required.')


#     def test_call_view_fails_invalid(self):
#         # same again, but with valid data, then
#         self.assertRedirects(response, '/contact/1/calls/')

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_submits_valid_data(self):
        data = {
            'username': self.username,
            'password': self.password,
        }
        response = self.client.post(reverse('login'), data)

        # Check it's a successful POST (200 OK) to the dashboard page
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)

    def test_activate_page_valid(self):
        user = self.create_user(is_active=False)
        response = self.client.get('/activate/?id='+str(user.pk*settings.SCALAR))
        self.assertEqual(response.status_code, 200)        
        self.assertIsInstance(response, HttpResponse)
        self.assertTemplateUsed(response, 'registration/activate.html')

    def test_activate_page_invalid(self):
        user = self.create_user(is_active=False)
        response = self.client.get('/activate/?id='+str(user.pk))
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response, HttpResponse)
        self.assertTemplateUsed(response, 'registration/activate.html')

    # TODO: NOT WORKING
    def test_activate_page_(self):
        user = self.create_user()
        response = self.client.post('activate/', {'id': user.id*570})
        # self.assertTrue(user.is_active)
        self.assertEqual(response.status_code, 200)

####################################
###         MAIN PAGES          ### 
####################################


    def test_thankyou_page_loads(self):
        data = {}
        response = self.client.get(reverse('thankyou'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)
        self.assertTemplateUsed(response, 'registration/thankyou.html')

    # def test_thankyou_page_redirects(self):
    #     pass

    def test_get_started_page_loads(self):
        self.log_user_in()
        response = self.client.get(reverse('get_started'))
        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponse)

    def test_get_started_page_redirects(self):
        self.log_user_in()
        response = self.client.post(reverse('get_started'))
        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponseRedirect)
        # self.assertTemplateUsed(response, 'main/get_started.html')





# TODO
    # def test_vendor_invoices_ajax(self):
    #     buyer_co = self.create_buyerCo
    #     vendor_co = self.create_vendorCo

    #     self.assertIsInstance(response, HttpResponseRedirect)


    # self.assertRedirects(response, reverse('thankyou'))

# GET REQUESTS
# def test_book_detail(self):
#     testbook = Book.objects.all()[0]
#     url = '/books/id/' + str(testbook.id)
#     response = self.client.get(url)
#     self.assertContains(response, testbook.title)

# BAD URL
# badurl = '/books/id/notabookid'
# response = self.client.get(badurl)
# self.assertContains(response, "Book not found", status_code=404)



# POST REQUESTS
# def test_addbook(self):
#     url = '/books/add/'

#     author = Author.objects.all()[0]    
#     user = author.user

#     # User not logged in
#     response = self.client.get(url)
#     self.assertEqual(response.status_code, 403)

#     self.client.login(username=user.username, password='password')

#     # Valid user
#     response = self.client.get(url)
#     self.assertEqual(response.status_code, 200)

#     # Invalid Form
#     response = self.client.post(url, {'title': "Book Title",
#                                       'author_id': author.id,
#                                       'ISBN': "invalid ISBN"})
#     self.assertFormError(response, 
#                          "BookSubmitForm", 
#                          'ISBN',
#                          "ISBN field must contain a number")

#     # Valid submission
#     newid = Book.objects.aggregate(Max('id'))['id__max'] + 1
#     redirect = '/books/id/%d' % newid
#     response = self.client.post(url, {'title': "Test book",
#                                       'author_id': author.id,
#                                       'ISBN': 123456},
#                                       follow=True)

#     self.assertRedirects(response, redirect)
#     self.assertContains(response, "Test book")

# class ViewTestCase(TestCase):

 
 # def test_whatever_list_view(self):
 #        w = self.create_whatever()
 #        url = reverse("whatever.views.whatever")
 #        resp = self.client.get(url)

 #        self.assertEqual(resp.status_code, 200)
 #        self.assertIn(w.title, resp.content)


 # def test_detail(self):
 #      resp = self.client.get('/polls/1/')
 #      self.assertEqual(resp.status_code, 200)
 #      self.assertEqual(resp.context['poll'].pk, 1)
 #      self.assertEqual(resp.context['poll'].question, 'Are you learning about testing in Django?')

 #      # Ensure that non-existent polls throw a 404.
 #      resp = self.client.get('/polls/2/')
 #      self.assertEqual(resp.status_code, 404)


# GET or POST by anonymous user (should redirect to login page)
# GET or POST by logged-in user with no profile (should raise a UserProfile.DoesNotExist exception)
# GET by logged-in user (should show the form)
# POST by logged-in user with blank data (should show form errors)
# POST by logged-in user with invalid data (should show form errors)
# POST by logged-in user with valid data (should redirect)
#  class TestCalls(TestCase):
#     def test_call_view_denies_anonymous(self):
#         response = self.client.get('/url/to/view', follow=True)
#         self.assertRedirects(response, '/login/')
#         response = self.client.post('/url/to/view', follow=True)
#         self.assertRedirects(response, '/login/')

#     def test_call_view_loads(self):
#         self.client.login(username='user', password='test')  # defined in fixture or with factory in setUp()
#         response = self.client.get('/url/to/view')
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'conversation.html')

#     def test_call_view_fails_blank(self):
#         self.client.login(username='user', password='test')
#         response = self.client.post('/url/to/view', {}) # blank data dictionary
#         self.assertFormError(response, 'form', 'some_field', 'This field is required.')
#         # etc. ...

#     def test_call_view_fails_invalid(self):
#         # as above, but with invalid rather than blank data in dictionary

#     def test_call_view_fails_invalid(self):
#         # same again, but with valid data, then
#         self.assertRedirects(response, '/contact/1/calls/')