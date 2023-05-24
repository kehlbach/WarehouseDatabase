from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import OuterRef, Subquery
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *
from .filters import *


class CustomViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, RequesterFilterBackend]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('id')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, DepartmentsFilterBackend,RequesterFilterBackend]
    filterset_fields = ['name']
    


class RolePermissionViewSet(CustomViewSet):
    queryset = RolePermission.objects.all().order_by('id')
    serializer_class = RolePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['role', 'action', 'subject']


class ActionsView(APIView):
    def get(self, request):
        return Response(dict(RolePermission.Actions))


class SubjectsView(APIView):
    def get(self, request):
        return Response(dict(RolePermission.Subjects))


class RoleViewSet(CustomViewSet):
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name']


class ProfileViewSet(CustomViewSet):
    queryset = Profile.objects.all().order_by('id')
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['phone_number', 'role', 'user_id']


class CategoryViewSet(CustomViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name']


class ProductViewSet(CustomViewSet):
    queryset = Product.objects.all().order_by('name').order_by('category__name')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['vendor_code', 'name', 'category']


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all().order_by('-id')
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [RequesterFilterBackend, DjangoFilterBackend, ReceiptsFilterBackend]
    filterset_fields = ['date', 'from_department', 'to_department', 'made_by']

class ReceiptProductViewSet(CustomViewSet):
    queryset = ReceiptProduct.objects.all().order_by('id')
    serializer_class = ReceiptProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['receipt', 'product']

    def destroy(self, request, pk=None):
        print('ReceiptProduct destroy!!')
        rp = self.get_object()
        try:
            if rp.receipt.from_department:
                latest_inventory = Inventory.objects.filter(
                    department=rp.receipt.from_department,
                    product=rp.product
                ).order_by('-year', '-month').first()
                inventory = Inventory.objects.get(
                    department=rp.receipt.from_department,
                    year=rp.receipt.date.year,
                    month=rp.receipt.date.month,
                    product=rp.product,)
                if inventory != latest_inventory:
                    raise ValidationError(
                        'Can\'t delete non-latest Receipt Product'
                    )
                inventory.goods_issued -= rp.quantity
                if inventory.goods_issued == 0 and inventory.goods_received == 0:
                    inventory.delete()
                else:
                    inventory.save()
            if rp.receipt.to_department:
                latest_inventory = Inventory.objects.filter(
                    department=rp.receipt.to_department,
                    product=rp.product
                ).order_by('-year', '-month').first()
                inventory = Inventory.objects.get(
                    department=rp.receipt.to_department,
                    year=rp.receipt.date.year,
                    month=rp.receipt.date.month,
                    product=rp.product,)
                if inventory != latest_inventory:
                    raise ValidationError(
                        'Can\'t delete non-latest Receipt Product'
                    )
                inventory.goods_received -= rp.quantity
                if inventory.goods_issued == 0 and inventory.goods_received == 0:
                    inventory.delete()
                else:
                    inventory.save()
        except ValidationError as e:
            print(e)
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
        rp.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InventoryViewSet(CustomViewSet):
    queryset = Inventory.objects.all().order_by('-year', '-month')
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'year', 'month', 'product']


class InventorySummaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventorySummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, RequesterFilterBackend]
    filterset_fields = ['department', 'product']

    def get_queryset(self):
        date_str = self.request.query_params.get('date', None)  # type: ignore
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            year, month = date.year, date.month
            grouped_records = Inventory.objects.filter(year=year, month__lte=month).values('department', 'product').annotate(
                latest_id=Subquery(
                    Inventory.objects.filter(
                        department=OuterRef('department'),
                        product=OuterRef('product'),
                        year=year,
                        month__lte=month
                    ).order_by('-year', '-month').values('id')[:1]
                )
            )
            if grouped_records.exists():
                latest_records = Inventory.objects.filter(id__in=Subquery(
                    grouped_records.values('latest_id'))).order_by('department', 'product')
            else:
                grouped_records = Inventory.objects.filter(year__lt=year).values('department', 'product').annotate(
                    latest_id=Subquery(
                        Inventory.objects.filter(
                            department=OuterRef('department'),
                            product=OuterRef('product'),
                            year__lt=year
                        ).order_by('-year', '-month').values('id')[:1]
                    )
                )
                if grouped_records.exists():
                    latest_records = Inventory.objects.filter(id__in=Subquery(
                        grouped_records.values('latest_id'))).order_by('department', 'product')
                else:
                    latest_records = Inventory.objects.none()
            return latest_records
        else:
            grouped_records = Inventory.objects.values('department', 'product').annotate(
                latest_id=Subquery(
                    Inventory.objects.filter(
                        department=OuterRef('department'),
                        product=OuterRef('product')
                    ).order_by('-year', '-month').values('id')[:1]
                )
            )
            latest_records = Inventory.objects.filter(id__in=Subquery(
                grouped_records.values('latest_id'))).order_by('department', 'product')
            return latest_records
