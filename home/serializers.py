# from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id','url', 'username', 'email', 'groups']


# class GroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = ['id','url', 'name']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
    # def create(self, validated_data):
    #     p = Permission.objects.create(**validated_data)
    #     admin = Role.objects.get_or_create(name='administrator')[0]
    #     all_perms = [perm.pk for perm in Permission.objects.all()]
    #     admin.save()
    #     admin.perms.add(*all_perms)
    #     return p


class RoleSerializer(serializers.ModelSerializer):
    #permissions = PermissionSerializer(many=True)
    class Meta:
        model = Role
        fields = '__all__'

# class RoleGetSerializer(serializers.ModelSerializer):
#     repr = serializers.SerializerMethodField()

#     def get_repr(self, obj):
#         return obj.repr
#     permissions = PermissionSerializer(many=True)

#     class Meta:
#         model = Role
#         fields = '__all__'


# class RoleSerializer(serializers.ModelSerializer):
#     repr = serializers.SerializerMethodField()

#     def get_repr(self, obj):
#         return obj.repr

#     class Meta:
#         model = Role
#         fields = '__all__'


# class ProfileGetSerializer(serializers.ModelSerializer):
#     repr = serializers.SerializerMethodField()

#     def get_repr(self, obj):
#         return obj.repr
#     role = RoleGetSerializer()

#     class Meta:
#         model = Profile
#         fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    #role = RoleSerializer()
    class Meta:
        model = Profile
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    #category = CategorySerializer()
    class Meta:
        model = Product
        fields = '__all__'

# class ProductGetSerializer(serializers.ModelSerializer):
#     repr = serializers.SerializerMethodField()

#     def get_repr(self, obj):
#         return obj.repr
#     category = CategorySerializer()

#     class Meta:
#         model = Product
#         fields = '__all__'


# class ProductSerializer(serializers.ModelSerializer):
#     repr = serializers.SerializerMethodField()

#     def get_repr(self, obj):
#         return obj.repr

#     class Meta:
#         model = Product
#         fields = '__all__'


    #from_department = DepartmentSerializer()
    #to_department = DepartmentSerializer()
    #made_by = ProfileSerializer()
# class ReceiptGetSerializer(serializers.ModelSerializer):
#     repr = serializers.SerializerMethodField()
#     type = serializers.SerializerMethodField()
#     def get_repr(self, obj):
#         return obj.repr
#     def get_type(self, obj):
#         return obj.type
#     from_department = DepartmentSerializer()
#     to_department = DepartmentSerializer()
#     made_by = ProfileSerializer()

#     class Meta:
#         model = Receipt
#         fields = '__all__'


# class ReceiptSerializer(serializers.ModelSerializer):
#     repr = serializers.SerializerMethodField()
#     type = serializers.SerializerMethodField()
#     def get_repr(self, obj):
#         return obj.repr
#     def get_type(self, obj):
#         return obj.type
#     class Meta:
#         model = Receipt
#         fields = '__all__'

    #receipt = ReceiptSerializer()
    #product = ProductSerializer()
# class ReceiptProductGetSerializer(serializers.ModelSerializer):
#     # repr = serializers.SerializerMethodField()
#     # def get_repr(self, obj):
#     #     return obj.repr
#     receipt = ReceiptGetSerializer()
#     product = ProductGetSerializer()

#     class Meta:
#         model = ReceiptProduct
#         fields = '__all__'


# class ReceiptProductSerializer(serializers.ModelSerializer):
#     # repr = serializers.SerializerMethodField()
#     # def get_repr(self, obj):
#     #     return obj.repr
#     class Meta:
#         model = ReceiptProduct
#         fields = '__all__'

#     def create(self, validated_data):
#         rp = ReceiptProduct.objects.create(**validated_data)
#         if rp.receipt.from_department:
#             inventory, created = Inventory.objects.get_or_create(
#                 department=rp.receipt.from_department,
#                 year=rp.receipt.date.year,
#                 month=rp.receipt.date.month,
#                 product=rp.product,
#             )
#             issued = rp.quantity
#             exists = inventory.month_start
#             receipts = Receipt.objects.filter(
#                 to_department = rp.receipt.from_department,
#                 date__year = rp.receipt.date.year,
#                 date__month = rp.receipt.date.month,
#                 date__day__lte = rp.receipt.date.day)
#             for each in receipts:
#                 obj = ReceiptProduct.objects.filter(
#                     receipt = each,
#                     product = rp.product
#                 ).first()
#                 exists += obj.quantity
#             if issued > exists:
#                 rp.delete()
#                 raise ValidationError('Not enough {} on department {}'.format(
#                     rp.product.repr,
#                     rp.receipt.from_department.repr))
#             if created:
#                 inventory.goods_issued = rp.quantity
#             else:  # existed
#                 inventory.goods_issued = F('goods_issued') + rp.quantity
#             inventory.save()
#         if rp.receipt.to_department:
#             inventory, created = Inventory.objects.get_or_create(
#                 department=rp.receipt.to_department,
#                 year=rp.receipt.date.year,
#                 month=rp.receipt.date.month,
#                 product=rp.product,
#             )
#             if created:
#                 inventory.goods_received = rp.quantity
#             else:  # existed
#                 inventory.goods_received = F('goods_received') + rp.quantity
#             inventory.save()
#         return rp

# class InventoryGetSerializer(serializers.ModelSerializer):
#     # repr = serializers.SerializerMethodField()
#     # def get_repr(self, obj):
#     #     return obj.repr
#     # department = DepartmentSerializer()
#     # product = ProductGetSerializer()
#     month_start = serializers.SerializerMethodField()

#     def get_month_start(self, obj):
#         return obj.month_start

#     class Meta:
#         model = Inventory
#         fields = '__all__'


# class InventorySerializer(serializers.ModelSerializer):
#     # repr = serializers.SerializerMethodField()
#     # def get_repr(self, obj):
#     #     return obj.repr
#     class Meta:
#         model = Inventory
#         fields = '__all__'
        # exclude = ('month_start',)

    # def update(self, instance, validated_data):
    #     instance.department = validated_data.get(
    #         'department', instance.department)
    #     instance.year = validated_data.get('year', instance.year)
    #     instance.month = validated_data.get('month', instance.month)
    #     instance.product = validated_data.get('product', instance.product)
    #     instance.month_start = validated_data.get(
    #         'month_start', instance.month_start)
    #     instance.goods_received = validated_data.get(
    #         'goods_received', instance.goods_received)
    #     instance.goods_issued = validated_data.get(
    #         'goods_issued', instance.goods_issued)
    #     instance.save()
    #     # invs = Inventory.objects.filter(
    #     #     product=instance.product,
    #     #     department=instance.department
    #     # )
    #     # for each in invs:
    #     #     if (each.year == instance.year and each.month > instance.month) or (each.year > instance.year):
    #     #         inv_from.goods_received = F('goods_received') + rp.quantity

    #     #         each =

    #     return instance
