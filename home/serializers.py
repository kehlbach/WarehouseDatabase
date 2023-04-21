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
    class Meta:
        model = Profile
        fields = '__all__'


    class Meta:
        model = Receipt
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    #     return instance
