from django.shortcuts import render

from django.contrib.auth.models import User, Group
from rest_framework.generics import RetrieveDestroyAPIView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .models import Profile
from .serializers import *

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('id')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name']

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all().order_by('id')
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['action', 'subject']


class ActionsView(APIView):
    def get(self, request):
        return Response(dict(Permission.Actions))

class SubjectsView(APIView):
    def get(self, request):
        return Response(dict(Permission.Subjects))

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name']

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['phone_number']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['vendor_code', 'name', 'category']

class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all().order_by('id')
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['date', 'from_department', 'to_department', 'made_by']

class ReceiptProductViewSet(viewsets.ModelViewSet):
    queryset = ReceiptProduct.objects.all().order_by('id')
    serializer_class = ReceiptProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['receipt', 'product']    
    def destroy(self,request, pk=None):
        rp = self.get_object()
        try:
            inventory = Inventory.objects.get(
            department=rp.receipt.from_department,
            year=rp.receipt.date.year,
            month=rp.receipt.date.month,
            product=rp.product,)
            if rp.receipt.from_department:        
                inventory.goods_received = F('goods_issued') - rp.quantity
            if rp.receipt.to_department:        
                inventory.goods_issued = F('goods_issued') - rp.quantity
            inventory.save()
        except Exception as e:
            print(e)
        rp.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all().order_by('-year', '-month')
    serializer_class = InventorySerializer
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]

