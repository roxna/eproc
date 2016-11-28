from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.utils import timezone
from eProc.models import *

class CompanyTest(TestCase):
	def create_instance(self, name="Test Name", currency="USD", website="http://www.test.com"):
        return Company.objects.create(name=name, currency=currency, website=website)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, Company))
        self.assertEqual(instance.__unicode__(), instance.name)


class BuyerCoTest(TestCase):
	def create_instance(self, name="Test Name", currency="USD", website="http://www.test.com"):
        return BuyerCo.objects.create(name=name, currency=currency, website=website)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, BuyerCo))
        self.assertTrue(isinstance(instance, Company))
        self.assertEqual(instance.__unicode__(), instance.name)

class VendorCoTest(TestCase):
	def create_instance(self, name="Test Name", currency="USD", website="http://www.test.com", contact_rep="Test Contact Rep", vendorID="1231F", buyer_co):
        return VendorCo.objects.create(name=name, currency=currency, website=website, contact_rep=contact_rep, vendorID=vendorID, buyer_co=BuyerCoTest.create_instance)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, VendorCo))
        self.assertTrue(isinstance(instance, Company))
        self.assertEqual(instance.__unicode__(), instance.name)


class LocationTest(TestCase):
	def create_instance(self, loc_type='Billing', address1='test_add1', address2='test_add2', city='test_city', state='test_state', county='test_country', zipcode='1231', phone='123131', email="test@email.com", company):
        return Location.objects.create(loc_type=loc_type, address1=address1, address2=address2, city=city, state=state, county=country, zipcode=zipcode, phone=phone, email=email, company=Company.create_instance)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, Location))
        name = "{} \n {} \n {}, {} {}, {}".format(instance.address1, instance.address2, instance.city, instance.state, instance.zipcode, instance.country)
        self.assertEqual(instance.__unicode__(), name)

class DepartmentTest(TestCase):
	def create_instance(self, name="Test Dept", company):
        return Department.objects.create(name=name, company=BuyerCo.create_instance)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, Department))
        self.assertEqual(instance.__unicode__(), instance.name)

class AccountCodeTest(TestCase):
	def create_instance(self, code="1234", name="Test Dept", expense_type='Expense', company, department):
        return AccountCode.objects.create(code=code, name=name, expense_type=expense_type, company=BuyerCo.create_instance, department=Department.create_instance)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, AccountCode))
        name = "[{}] {}".format(instance.code, instance.name)
        self.assertEqual(instance.__unicode__(), name)


class TaxTest(TestCase):
	def create_instance(self, name='Test Tax', percent=15.0):
        return Tax.objects.create(name=name, percent=percent)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, Tax))
        name = "{} ({}%)".format(instance.name, instance.percent)
        self.assertEqual(instance.__unicode__(), name)

class UserTest(TestCase):
	def create_instance(self, username='Test Username', password='Test PW'):
        return User.objects.create(username=username, password=password)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, User))
        self.assertEqual(instance.__unicode__(), instance.username)

class BuyerProfileTest(TestCase):
	def create_instance(self, role='SuperUser', user, department, company):
        return BuyerProfile.objects.create(role=role, user=User.create_instance, department=Department.create_instance, company=BuyerCo.create_instance)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, BuyerProfile))
        self.assertEqual(instance.__unicode__(), instance.user.name)

class VendorProfileTest(TestCase):
	def create_instance(self, user, company):
        return VendorProfile.objects.create(user=User.create_instance, company=VendorCo.create_instance)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, VendorProfile))
        self.assertEqual(instance.__unicode__(), instance.user.name)


class RequisitionTest(TestCase):
	def create_instance(self, number="RO1", date_issued=timezone.now, preparer, next_approver, buyer_co, department):
        return Requisition.objects.create(number=number, date_issued=date_issued, preparer=BuyerProfile.create_instance, next_approver=BuyerProfile.create_instance, buyer_co=BuyerCo.create_instance, department=Department.create_instance)

    def test_instance_creation(self):
        instance = self.create_instance()
        self.assertTrue(isinstance(instance, Requisition))
        self.assertEqual(instance.__unicode__(), instance.name)

class PurchaseOrderTest(TestCase):
	pass

class InvoiceTest(TestCase):
	pass

class FileTest(TestCase):
	pass

class CategoryTest(TestCase):
	pass

class CatalogItemTest(TestCase):
	pass

class OrderItemTest(TestCase):
	pass

class StatusTest(TestCase):
	pass

class RatingTest(TestCase):
	pass




