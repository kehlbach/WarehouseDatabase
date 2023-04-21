from django.core.exceptions import ValidationError
from django.db.models import F
from rest_framework import serializers

from .models import *


class DepartmentSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    class Meta:
        model = Department
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    class Meta:
        model = Permission
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    class Meta:
        model = Role
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr
    permissions = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = '__all__'

    def get_permissions(self, obj):
        return ' '.join(str(i.id) for i in Role.objects.get(id=obj.role.id).permissions.get_queryset())

    def get_role_name(self, obj):
        return obj.role.repr


class CategorySerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    class Meta:
        model = Product
        fields = '__all__'


class ReceiptSerializer(serializers.ModelSerializer):
    repr = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_repr(self, obj):
        return obj.repr

    def get_type(self, obj):
        return obj.type

    class Meta:
        model = Receipt
        fields = '__all__'


class ReceiptProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptProduct
        fields = '__all__'

    def create(self, validated_data):
        rp = ReceiptProduct.objects.create(**validated_data)
        if rp.receipt.from_department:
            inventory, created = Inventory.objects.get_or_create(
                department=rp.receipt.from_department,
                year=rp.receipt.date.year,
                month=rp.receipt.date.month,
                product=rp.product,)
            issued = rp.quantity
            exists = inventory.month_start
            receipts = Receipt.objects.filter(
                to_department=rp.receipt.from_department,
                date__year=rp.receipt.date.year,
                date__month=rp.receipt.date.month,
                date__day__lte=rp.receipt.date.day)
            for each in receipts:
                obj = ReceiptProduct.objects.filter(
                    receipt=each,
                    product=rp.product).first()
                if obj:
                    exists += obj.quantity
            if issued > exists:
                rp.delete()
                raise ValidationError('Not enough {} on department {}'.format(
                    rp.product.repr,
                    rp.receipt.from_department.repr))
            if created:
                inventory.goods_issued = rp.quantity
            else:  # existed
                inventory.goods_issued = F('goods_issued') + rp.quantity
            inventory.save()
        if rp.receipt.to_department:
            inventory, created = Inventory.objects.get_or_create(
                department=rp.receipt.to_department,
                year=rp.receipt.date.year,
                month=rp.receipt.date.month,
                product=rp.product,)
            if created:
                inventory.goods_received = rp.quantity
            else:  # existed
                inventory.goods_received = F('goods_received') + rp.quantity
            inventory.save()
        return rp


class InventorySerializer(serializers.ModelSerializer):
    month_start = serializers.SerializerMethodField()

    def get_month_start(self, obj):
        return obj.month_start

    class Meta:
        model = Inventory
        fields = '__all__'
