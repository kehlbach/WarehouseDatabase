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

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        model = Product
        fields = '__all__'


    class Meta:
        model = Receipt
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    #     return instance
