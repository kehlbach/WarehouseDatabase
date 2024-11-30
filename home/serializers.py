import json
from datetime import datetime

from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import *


class DepartmentSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()
    receipts_count = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    def get_receipts_count(self, obj):
        return obj.receipts_count

    class Meta:
        model = Department
        fields = "__all__"


class RolePermissionSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    class Meta:
        model = RolePermission
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()
    permissions_repr = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    class Meta:
        model = Role
        fields = "__all__"

    def get_permissions(self, obj):
        subjects = dict(RolePermission.Subjects).keys()
        result = []
        permissions_by_subj = RolePermission.objects.filter(role=obj)
        for subject in subjects:
            permissions_by_subj = RolePermission.objects.filter(
                role=obj, subject=subject
            )
            result.append([subject, [obj.action for obj in permissions_by_subj]])
        return json.dumps(result)

    def get_permissions_repr(self, obj):
        subjects = dict(RolePermission.Subjects).keys()
        value = ""
        for each in subjects:
            _subjects = dict(RolePermission.Subjects)
            _actions = dict(RolePermission.Actions)
            permissions_by_subj = RolePermission.objects.filter(
                role=obj.id, subject=each
            )
            value += (
                f"{_subjects[each]}:"
                + ",".join([_actions[obj.action] for obj in permissions_by_subj])
                + " "
            )  # type: ignore
        return value


class ProfileSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    permissions = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = "__all__"

    def get_permissions(self, obj):
        subjects = dict(RolePermission.Subjects).keys()
        result = []
        permissions_by_subj = RolePermission.objects.filter(role=obj.role)
        for subject in subjects:
            permissions_by_subj = RolePermission.objects.filter(
                role=obj.role, subject=subject
            )
            result.append([subject, [obj.action for obj in permissions_by_subj]])
        return json.dumps(result)

    def get_role_name(self, obj):
        return obj.role.repr


class CategorySerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    class Meta:
        model = Product
        fields = "__all__"

    def get_category_name(self, obj):
        if obj.category:
            return obj.category.name
        else:
            return ""


class ReceiptSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    from_department_name = serializers.SerializerMethodField()
    to_department_name = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    def get_type(self, obj):
        return obj.type

    def get_from_department_name(self, obj):
        if obj.from_department:
            return obj.from_department.name
        else:
            return ""

    def get_to_department_name(self, obj):
        if obj.to_department:
            return obj.to_department.name
        else:
            return ""

    class Meta:
        model = Receipt
        fields = "__all__"


class ReceiptProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptProduct
        fields = "__all__"

    product_name = serializers.SerializerMethodField()
    product_units = serializers.SerializerMethodField()

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_units(self, obj):
        return obj.product.units

    def create(self, validated_data):
        quantity = validated_data.get("quantity", 0)
        product_id = validated_data.get("product_id")
        if quantity == 0:
            # If quantity is 0, delete an existing object if one exists and do not create a new one
            existing_instance = ReceiptProduct.objects.filter(
                product_id=product_id
            ).first()
            if existing_instance:
                existing_instance.delete()
            return
        else:
            # If quantity is not 0, create a new object
            rp = ReceiptProduct.objects.create(**validated_data)
        if rp.receipt.from_department:
            inventory, created = Inventory.objects.get_or_create(
                department=rp.receipt.from_department,
                year=rp.receipt.date.year,
                month=rp.receipt.date.month,
                product=rp.product,
            )
            issued = rp.quantity
            exists = inventory.month_start
            receipts_to_department = Receipt.objects.filter(
                to_department=rp.receipt.from_department,
                date__year=rp.receipt.date.year,
                date__month=rp.receipt.date.month,
                date__day__lte=rp.receipt.date.day,
            )
            for each in receipts_to_department:
                obj = ReceiptProduct.objects.filter(
                    receipt=each, product=rp.product
                ).first()
                if obj and obj != rp:
                    exists += obj.quantity
            receipts_from_department = Receipt.objects.filter(
                from_department=rp.receipt.from_department,
                date__year=rp.receipt.date.year,
                date__month=rp.receipt.date.month,
                date__day__lte=rp.receipt.date.day,
            )
            for each in receipts_from_department:
                obj = ReceiptProduct.objects.filter(
                    receipt=each, product=rp.product
                ).first()
                if obj and obj != rp:
                    exists -= obj.quantity
            if issued > exists:
                _product_name = rp.product.repr
                department_name = rp.receipt.from_department.repr
                text = "Not enough {} on department {}".format(
                    _product_name, department_name
                )
                rp.delete()
                raise ValidationError(text)
            if created:
                inventory.goods_issued = rp.quantity
            else:
                inventory.goods_issued += rp.quantity
            inventory.save()
        if rp.receipt.to_department:
            inventory, created = Inventory.objects.get_or_create(
                department=rp.receipt.to_department,
                year=rp.receipt.date.year,
                month=rp.receipt.date.month,
                product=rp.product,
            )
            if created:
                inventory.goods_received = rp.quantity
            else:
                inventory.goods_received += rp.quantity
            inventory.save()
        return rp


class InventorySerializer(serializers.ModelSerializer):
    month_start = serializers.SerializerMethodField()

    def get_month_start(self, obj):
        return obj.month_start

    class Meta:
        model = Inventory
        fields = "__all__"


class InventorySummarySerializer(serializers.Serializer):
    department = serializers.IntegerField(source="department.id")
    department_name = serializers.SerializerMethodField()
    product = serializers.IntegerField(source="product.id")
    product_name = serializers.SerializerMethodField()
    product_units = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    def get_department_name(self, obj):
        return obj.department.name

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_units(self, obj):
        return obj.product.units

    def get_quantity(self, obj) -> int:
        date_str = self.context.get("request").query_params.get("date", None)  # type: ignore
        """
        Get the quantity of product in inventory on the given date.
        If no date is given, the quantity as of the last inventory is returned.

        :param obj: InventorySummary instance
        :return: quantity of product in inventory
        """
        # note: may require optimization of queries if performance is an issue
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            year, month = date.year, date.month
            latest = Inventory.objects.filter(
                department=obj.department,
                product=obj.product,
                year=year,
                month__lte=month,
            ).order_by("-year", "-month")
            if latest:
                # If there is an inventory in the given month, or closest previous month in given year, return the quantity
                return (
                    latest[0].month_start
                    + latest[0].goods_received
                    - latest[0].goods_issued
                )
            else:
                # If there is no inventory in the given year, get the latest inventory
                # for the given department and product for closest to given date prevoius year/month
                latest = Inventory.objects.filter(
                    department=obj.department, product=obj.product, year__lt=year
                ).order_by("-year", "-month")
                return (
                    latest[0].month_start
                    + latest[0].goods_received
                    - latest[0].goods_issued
                )
        else:
            # Get the latest inventory for the given department and product
            latest = Inventory.objects.filter(
                department=obj.department, product=obj.product
            ).order_by("-year", "-month")[0]
            return latest.month_start + latest.goods_received - latest.goods_issued

    class Meta:
        fields = ["department", "product", "quantity"]
