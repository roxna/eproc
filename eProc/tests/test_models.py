# from django.core.exceptions import ValidationError
# from django.core.urlresolvers import reverse
# from django.http import HttpResponseRedirect
# from django.test import TestCase
# from django.utils import timezone
# from eProc.models import *

# class CompanyTest(TestCase):
#     @classmethod
#     def create_instance():
#         return Company.objects.create(name="Test Name", currency="USD", website="http://www.test.com")

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, Company))
#         self.assertEqual(instance.__unicode__(), instance.name)


# class BuyerCoTest(TestCase):
#     @classmethod
#     def create_instance():
#         return BuyerCo.objects.create(name="Test Name", currency="USD", website="http://www.test.com")

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, BuyerCo))
#         self.assertTrue(isinstance(instance, Company))
#         self.assertEqual(instance.__unicode__(), instance.name)

# class VendorCoTest(TestCase):
#     @classmethod
#     def create_instance():
#         return VendorCo.objects.create(buyer_co=BuyerCoTest.create_instance(), name=name, currency=currency, website=website, contact_rep=contact_rep, vendorID=vendorID)

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, VendorCo))
#         self.assertTrue(isinstance(instance, Company))
#         self.assertEqual(instance.__unicode__(), instance.name)


# class LocationTest(TestCase):
#     # def create_instance(self, company, loc_type='Billing', address1='test_add1', address2='test_add2', city='test_city', state='test_state', county='test_country', zipcode='1231', phone='123131', email="test@email.com"):
#     def create_instance(self):
#         return Location.objects.create(company=CompanyTest().create_instance(), loc_type='Billing', address1='test_add1', address2='test_add2', city='test_city', state='test_state', county='test_country', zipcode='1231', phone='123131', email="test@email.com")

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, Location))
#         name = "{} \n {} \n {}, {} {}, {}".format(instance.address1, instance.address2, instance.city, instance.state, instance.zipcode, instance.country)
#         self.assertEqual(instance.__unicode__(), name)

# class DepartmentTest(TestCase):
#     def create_instance(self):
#         return Department.objects.create(company=BuyerCoTest.create_instance, name="Test Dept")

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, Department))
#         self.assertEqual(instance.__unicode__(), instance.name)

# class AccountCodeTest(TestCase):
#     def create_instance(self, company, department, code="1234", name="Test Dept", expense_type='Expense'):
#         return AccountCode.objects.create(company=BuyerCoTest.create_instance, department=DepartmentTest.create_instance, code=code, name=name, expense_type=expense_type)

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, AccountCode))
#         name = "[{}] {}".format(instance.code, instance.name)
#         self.assertEqual(instance.__unicode__(), name)


# class TaxTest(TestCase):
#     def create_instance(self, name='Test Tax', percent=15.0):
#         return Tax.objects.create(name=name, percent=percent)

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, Tax))
#         name = "{} ({}%)".format(instance.name, instance.percent)
#         self.assertEqual(instance.__unicode__(), name)

# class UserTest(TestCase):
#     def create_instance(self, username='Test Username', password='Test PW'):
#         return User.objects.create(username=username, password=password)

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, User))
#         self.assertEqual(instance.__unicode__(), instance.username)

# class BuyerProfileTest(TestCase):
#     def create_instance(self, user, department, company, role='SuperUser'):
#         return BuyerProfile.objects.create(user=UserTest.create_instance, department=DepartmentTest.create_instance, company=BuyerCoTest.create_instance, role=role, )

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, BuyerProfile))
#         self.assertEqual(instance.__unicode__(), instance.user.name)

# class VendorProfileTest(TestCase):
#     def create_instance(self, user, company):
#         return VendorProfile.objects.create(user=UserTest.create_instance, company=VendorCoTest.create_instance)

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, VendorProfile))
#         self.assertEqual(instance.__unicode__(), instance.user.name)


# class RequisitionTest(TestCase):
#     def create_instance(self, preparer, next_approver, buyer_co, department, number="RO1", date_issued=timezone.now):
#         return Requisition.objects.create(preparer=BuyerProfileTest.create_instance, next_approver=BuyerProfileTest.create_instance, buyer_co=BuyerCoTest.create_instance, department=DepartmentTest.create_instance, number=number, date_issued=date_issued)

#     def test_instance_creation(self):
#         instance = self.create_instance()
#         self.assertTrue(isinstance(instance, Requisition))
#         self.assertEqual(instance.__unicode__(), instance.name)

# class PurchaseOrderTest(TestCase):
#     pass

# class InvoiceTest(TestCase):
#     pass

# class FileTest(TestCase):
#     pass

# class CategoryTest(TestCase):
#     pass

# class CatalogItemTest(TestCase):
#     pass

# class OrderItemTest(TestCase):
#     pass

# class StatusTest(TestCase):
#     pass

# class RatingTest(TestCase):
#     pass




