from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.urls import reverse
import phonenumbers
from rest_framework import status
from rest_framework.test import APITestCase
from home.models import (
    Category,
    Product,
    Receipt,
    ReceiptProduct,
    Inventory,
    Department,
    Role,
    Profile,
    RolePermission,
)


class Test(APITestCase):
    def setUp(self):
        self.user_credentials = {"username": "admin", "password": "admin"}
        self.user = User.objects.create_user(**self.user_credentials)

    def test_create_category(self):
        self.client.login(**self.user_credentials)
        data = {"name": "Cars"}
        response = self.client.post(reverse("category-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name=data["name"]).exists())

    def test_delete_category(self):
        self.client.login(**self.user_credentials)
        category = Category.objects.create(name="Cars")
        response = self.client.delete(reverse("category-detail", args=[category.id]))  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_create_product(self):
        self.client.login(**self.user_credentials)
        category = Category.objects.create(name="Cars")
        data = {"name": "Some Car", "category": category.id}
        response = self.client.post(reverse("product-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["category"], category.id)
        self.assertEqual(response.data["units"], "pcs")
        self.assertEqual(Product.objects.count(), 1)

    def test_delete_product(self):
        self.client.login(**self.user_credentials)
        category = Category.objects.create(name="Cars")
        product = Product.objects.create(name="Some Car", category=category)
        response = self.client.delete(reverse("product-detail", args=[product.id]))  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_category_with_products(self):
        self.client.login(**self.user_credentials)
        category = Category.objects.create(name="test")
        product = Product.objects.create(name="test", category=category)
        with self.assertRaises(ProtectedError):
            response = self.client.delete(reverse("category-detail", args=[category.id]))  # type: ignore
            if response.status_code != ProtectedError:
                self.fail("Category with products should be not deletable")
        self.assertTrue(Category.objects.filter(id=category.id).exists())

    def test_create_department(self):
        self.client.login(**self.user_credentials)
        data = {"name": "Testing Department"}
        response = self.client.post(reverse("department-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Department.objects.filter(name=data["name"]).exists())
        self.assertEqual(response.data["location"], "")
        self.assertEqual(response.data["receipts_count"], 0)

    def test_delete_department(self):
        self.client.login(**self.user_credentials)
        department = Department.objects.create(name="Testing Department")
        response = self.client.delete(reverse("department-detail", args=[department.id]))  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Department.objects.filter(id=department.id).exists())

    def test_create_role(self):
        self.client.login(**self.user_credentials)
        data = {"name": "Test Role"}
        response = self.client.post(reverse("role-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(name=data["name"]).exists())

    def test_delete_role(self):
        self.client.login(**self.user_credentials)
        role = Role.objects.create(name="Test Role")
        response = self.client.delete(reverse("role-detail", args=[role.id]))  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Role.objects.filter(id=role.id).exists())

    def test_create_profile(self):
        self.client.login(**self.user_credentials)
        role = Role.objects.create(name="Test Role")
        data = {"phone_number": "+12345678912", "role": 1}
        response = self.client.post(reverse("profile-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        parsed_number = phonenumbers.parse(response.data["phone_number"])
        prepared_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        self.assertTrue(Profile.objects.filter(phone_number=prepared_number).exists())
        self.assertEqual(response.data["role"], data["role"])
