from datetime import datetime, timedelta

import phonenumbers
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from home.models import (
    Category,
    Department,
    Inventory,
    Product,
    Profile,
    Receipt,
    ReceiptProduct,
    Role,
    RolePermission,
)

# To do next:
# 1. Add tests for InventorySummary
# 2. Add tests involving filters
# (separately or incorporate into existing tests?)


user_credentials = {"username": "admin", "password": "admin"}
User = get_user_model()


class ProductTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(**user_credentials)
        self.category = Category.objects.create(name="Cars")

    def test_create_product(self):
        self.client.login(**user_credentials)
        data = {"name": "Some Car", "category": self.category.id}
        response = self.client.post(reverse("product-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["category"], self.category.id)
        self.assertEqual(response.data["units"], "pcs")
        self.assertEqual(Product.objects.count(), 1)

    def test_delete_product(self):
        self.client.login(**user_credentials)
        product = Product.objects.create(name="Some Car", category=self.category)
        response = self.client.delete(reverse("product-detail", args=[product.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_product_with_receipts(self):
        self.client.login(**user_credentials)
        product = Product.objects.create(name="Some Car", category=self.category)
        role = Role.objects.create(name="Test Role")
        profile = Profile.objects.create(phone_number="+12345678912", role=role)
        to_department = Department.objects.create(name="Testing Department")
        receipt = Receipt.objects.create(made_by=profile, to_department=to_department)
        ReceiptProduct.objects.create(product=product, receipt=receipt, quantity=1)
        with self.assertRaises(ProtectedError):
            response = self.client.delete(reverse("product-detail", args=[product.id]))
            if response.status_code != ProtectedError:
                self.fail("Product with receipts should be not deletable")
        self.assertTrue(Product.objects.filter(id=product.id).exists())


class DepartmentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**user_credentials)

    def test_create_department(self):
        self.client.login(**user_credentials)
        data = {"name": "Testing Department"}
        base_url = reverse("department-list")
        role = Role.objects.create(name="Test Role")
        RolePermission.objects.create(
            role=role,
            action=RolePermission.ADD,
            subject=RolePermission.DEPARTMENTS,
        )
        profile = Profile.objects.create(
            phone_number="+12345678912", role=role, user_id="123"
        )
        modified_url = f"{base_url}?requester={profile.user_id}"
        response = self.client.post(modified_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["location"], "")
        self.assertEqual(response.data["receipts_count"], 0)
        self.assertTrue(
            Department.objects.get(id=response.data["id"]) in profile.departments.all()
        )
        self.assertEqual(Department.objects.count(), 1)

    def test_delete_department(self):
        self.client.login(**user_credentials)
        department = Department.objects.create(name="Testing Department")
        response = self.client.delete(
            reverse("department-detail", args=[department.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Department.objects.filter(id=department.id).exists())

    def test_delete_department_with_receipts(self):
        self.client.login(**user_credentials)
        role = Role.objects.create(name="Test Role")
        to_department = Department.objects.create(name="Testing Department")
        profile = Profile.objects.create(phone_number="+12345678912", role=role)
        profile.departments.add(to_department)
        Receipt.objects.create(to_department=to_department, made_by=profile)
        with self.assertRaises(ProtectedError):
            response = self.client.delete(
                reverse("department-detail", args=[to_department.id])
            )
            if response.status_code != ProtectedError:
                self.fail("Department with receipts should be not deletable")
        self.assertTrue(Department.objects.filter(id=to_department.id).exists())


class RoleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**user_credentials)
        self.action = RolePermission.VIEW
        self.subject = RolePermission.PRODUCTS

    def test_create_role(self):
        self.client.login(**user_credentials)
        data = {"name": "Test Role"}
        response = self.client.post(reverse("role-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(name=data["name"]).exists())

    def test_delete_role(self):
        self.client.login(**user_credentials)
        role = Role.objects.create(name="Test Role")
        response = self.client.delete(reverse("role-detail", args=[role.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Role.objects.filter(id=role.id).exists())

    def test_delete_role_with_permissions(self):
        self.client.login(**user_credentials)
        role = Role.objects.create(name="Test Role")
        role_permission = RolePermission.objects.create(
            role=role,
            action=RolePermission.VIEW,
            subject=RolePermission.PRODUCTS,
        )
        response = self.client.delete(reverse("role-detail", args=[role.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Role.objects.filter(id=role.id).exists())
        self.assertFalse(RolePermission.objects.filter(id=role_permission.id).exists())

    def test_create_role_permission(self):
        role = Role.objects.create(name="Test Role")
        self.client.login(**user_credentials)
        data = {
            "role": role.id,
            "action": self.action,
            "subject": self.subject,
        }
        response = self.client.post(reverse("rolepermission-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            RolePermission.objects.filter(
                role=role, action=self.action, subject=self.subject
            ).exists()
        )

    def delete_role_permission(self):
        role = Role.objects.create(name="Test Role")
        self.client.login(**user_credentials)
        role_permission = RolePermission.objects.create(
            role=role, action=self.action, subject=self.subject
        )
        response = self.client.delete(
            reverse("rolepermission-detail", args=[role_permission.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RolePermission.objects.filter(id=role_permission.id).exists())


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**user_credentials)
        self.role = Role.objects.create(name="Test Role")

    def test_create_profile(self):
        self.client.login(**user_credentials)
        data = {"phone_number": "+12345678912", "role": self.role.id}
        response = self.client.post(reverse("profile-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        parsed_number = phonenumbers.parse(response.data["phone_number"])
        prepared_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        self.assertTrue(Profile.objects.filter(phone_number=prepared_number).exists())
        self.assertEqual(response.data["role"], data["role"])

    def test_delete_profile(self):
        self.client.login(**user_credentials)
        profile = Profile.objects.create(phone_number="+12345678912", role=self.role)
        response = self.client.delete(reverse("profile-detail", args=[profile.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Profile.objects.filter(id=profile.id).exists())

    def test_delete_profile_with_receipts(self):
        self.client.login(**user_credentials)
        profile = Profile.objects.create(phone_number="+12345678912", role=self.role)
        Receipt.objects.create(made_by=profile)
        with self.assertRaises(ProtectedError):
            response = self.client.delete(reverse("profile-detail", args=[profile.id]))
            if response.status_code != ProtectedError:
                self.fail("Profile with receipts should be not deletable")
        self.assertTrue(Profile.objects.filter(id=profile.id).exists())


class CategoryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**user_credentials)

    def test_create_category(self):
        self.client.login(**user_credentials)
        data = {"name": "Cars"}
        response = self.client.post(reverse("category-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name=data["name"]).exists())

    def test_delete_category(self):
        self.client.login(**user_credentials)
        category = Category.objects.create(name="Cars")
        response = self.client.delete(reverse("category-detail", args=[category.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_delete_category_with_products(self):
        self.client.login(**user_credentials)
        category = Category.objects.create(name="test")
        Product.objects.create(name="test", category=category)
        with self.assertRaises(ProtectedError):
            response = self.client.delete(
                reverse("category-detail", args=[category.id])
            )
            if response.status_code != ProtectedError:
                self.fail("Category with products should be not deletable")
        self.assertTrue(Category.objects.filter(id=category.id).exists())


class ReceiptTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**user_credentials)
        self.profile = Profile.objects.create(
            phone_number="+12345678912",
            role=Role.objects.create(name="Test Role"),
        )
        self.department_one = Department.objects.create(name="Testing Department")
        self.product = Product.objects.create(
            name="Some Car", category=Category.objects.create(name="Cars")
        )

    def test_create_empty_receipt(self):
        self.client.login(**user_credentials)
        data = {
            "made_by": self.profile.id,
            "to_department": self.department_one.id,
        }
        response = self.client.post(reverse("receipt-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Receipt.objects.filter(
                made_by=self.profile, to_department=self.department_one
            ).exists()
        )

    def test_delete_empty_receipt(self):
        self.client.login(**user_credentials)
        receipt = Receipt.objects.create(
            made_by=self.profile, to_department=self.department_one
        )
        response = self.client.delete(reverse("receipt-detail", args=[receipt.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Receipt.objects.filter(id=receipt.id).exists())

    def test_create_receipt(self):
        # covsrs:
        # adding product to dep. one (incoming receipt)
        # moving product from dep. one to dep. two (transfer receipt)
        # removing product from dep. one (outgoing receipt)
        self.client.login(**user_credentials)
        receipt_incoming = Receipt.objects.create(
            made_by=self.profile, to_department=self.department_one
        )
        response = self.client.post(
            reverse("receiptproduct-list"),
            {
                "receipt": receipt_incoming.id,
                "product": self.product.id,
                "quantity": 3,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ReceiptProduct.objects.filter(
                receipt=receipt_incoming, product=self.product
            ).exists()
        )
        inv_dep_one = Inventory.objects.filter(
            department=receipt_incoming.to_department,
            year=receipt_incoming.date.year,
            month=receipt_incoming.date.month,
            product=self.product,
        ).first()
        # incoming check
        self.assertEqual(inv_dep_one.goods_received, 3)
        self.assertEqual(inv_dep_one.goods_issued, 0)
        self.assertEqual(inv_dep_one.month_start, 0)

        department_two = Department.objects.create(name="Testing Department 2")
        receipt_transfer = Receipt.objects.create(
            made_by=self.profile,
            from_department=self.department_one,
            to_department=department_two,
        )
        response = self.client.post(
            reverse("receiptproduct-list"),
            {
                "receipt": receipt_transfer.id,
                "product": self.product.id,
                "quantity": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        inv_dep_two = Inventory.objects.filter(
            department=receipt_transfer.to_department,
            year=receipt_incoming.date.year,
            month=receipt_incoming.date.month,
            product=self.product,
        ).first()
        # transfer check
        inv_dep_one.refresh_from_db()
        self.assertEqual(inv_dep_one.goods_received, 3)
        self.assertEqual(inv_dep_one.goods_issued, 1)
        self.assertEqual(inv_dep_one.month_start, 0)
        self.assertEqual(inv_dep_two.goods_received, 1)
        self.assertEqual(inv_dep_two.goods_issued, 0)
        self.assertEqual(inv_dep_two.month_start, 0)

        receipt_outgoing = Receipt.objects.create(
            made_by=self.profile, from_department=self.department_one
        )
        response = self.client.post(
            reverse("receiptproduct-list"),
            {
                "receipt": receipt_outgoing.id,
                "product": self.product.id,
                "quantity": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # outgoing check
        inv_dep_one.refresh_from_db()
        self.assertEqual(inv_dep_one.goods_received, 3)
        self.assertEqual(inv_dep_one.goods_issued, 2)
        self.assertEqual(inv_dep_one.month_start, 0)

    def test_receipts_different_months(self):
        self.client.login(**user_credentials)
        two_months_ago = datetime.today() - timedelta(days=60)
        receipt_incoming_one = Receipt.objects.create(
            made_by=self.profile,
            to_department=self.department_one,
            date=two_months_ago.date(),
        )
        self.client.post(
            reverse("receiptproduct-list"),
            {
                "receipt": receipt_incoming_one.id,
                "product": self.product.id,
                "quantity": 3,
            },
        )
        receipt_incoming_two = Receipt.objects.create(
            made_by=self.profile, to_department=self.department_one
        )
        self.client.post(
            reverse("receiptproduct-list"),
            {
                "receipt": receipt_incoming_two.id,
                "product": self.product.id,
                "quantity": 1,
            },
        )
        inv_two_months_ago = Inventory.objects.filter(
            department=receipt_incoming_one.to_department,
            year=receipt_incoming_one.date.year,
            month=receipt_incoming_one.date.month,
            product=self.product,
        ).first()
        inv_current = Inventory.objects.filter(
            department=receipt_incoming_two.to_department,
            year=receipt_incoming_two.date.year,
            month=receipt_incoming_two.date.month,
            product=self.product,
        ).first()
        self.assertEqual(inv_two_months_ago.goods_received, 3)
        self.assertEqual(inv_two_months_ago.goods_issued, 0)
        self.assertEqual(inv_two_months_ago.month_start, 0)
        self.assertEqual(inv_current.goods_received, 1)
        self.assertEqual(inv_current.goods_issued, 0)
        self.assertEqual(inv_current.month_start, 3)

    def test_delete_receipt(self):
        self.client.login(**user_credentials)
        receipt_one = Receipt.objects.create(
            made_by=self.profile, to_department=self.department_one
        )
        receipt_two = Receipt.objects.create(
            made_by=self.profile, to_department=self.department_one
        )
        # When creation/saving/etc of instance is modified
        # in serializers/views, this is the way to work with object,
        # so code from all three models,serializers,views)
        # would be executed.
        self.client.post(
            reverse("receiptproduct-list"),
            {
                "receipt": receipt_one.id,
                "product": self.product.id,
                "quantity": 3,
            },
        )
        rp_two_response = self.client.post(
            reverse("receiptproduct-list"),
            {
                "receipt": receipt_two.id,
                "product": self.product.id,
                "quantity": 1,
            },
        )
        # Deleting receipt with receipt products
        with self.assertRaises(ProtectedError):
            response = self.client.delete(
                reverse("receipt-detail", args=[receipt_two.id])
            )
            if response.status_code != ProtectedError:
                self.fail("Receipt with receipt products should be not deletable")
        # Deleting non-latest receipt
        with self.assertRaises(ProtectedError):
            response = self.client.delete(
                reverse("receipt-detail", args=[receipt_one.id])
            )
            if response.status_code != ProtectedError:
                self.fail("Non-latest receipt should be not deletable")
        self.assertTrue(Receipt.objects.filter(id=receipt_one.id).exists())
        self.assertTrue(Receipt.objects.filter(id=receipt_two.id).exists())
        rp_delete_response = self.client.delete(
            reverse("receiptproduct-detail", args=[rp_two_response.data["id"]])
        )
        self.assertEqual(rp_delete_response.status_code, status.HTTP_204_NO_CONTENT)
        receipt_delete_response = self.client.delete(
            reverse("receipt-detail", args=[receipt_two.id])
        )
        self.assertEqual(
            receipt_delete_response.status_code, status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(Receipt.objects.filter(id=receipt_two.id).exists())
        self.assertEqual(Inventory.objects.count(), 1)
        self.assertEqual(Inventory.objects.first().goods_received, 3)
