from datetime import datetime, timedelta
from datetime import datetime
from django.db.models import OuterRef, Subquery, Sum
from django.db.models import F, Sum
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


class RolePermissionViewSet(viewsets.ModelViewSet):
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


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name']


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by('id')
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['phone_number', 'role', 'user_id']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['vendor_code', 'name', 'category']


from rest_framework.test import APIRequestFactory

class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all().order_by('id')
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['date', 'from_department', 'to_department', 'made_by']
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     receipt_products = instance.receiptproduct_set.all()
    #     for receipt_product in receipt_products:
    #         # Convert rest_framework.request.Request to django.http.HttpRequest
    #         factory = APIRequestFactory()
    #         request = factory.delete('/')
    #         request = self.initialize_request(request)
    #         # Call the destroy method of ReceiptProductViewSet
    #         ReceiptProductViewSet.as_view({'delete': 'destroy'})(
    #             request, pk=receipt_product.pk)
    #     return super().destroy(request, *args, **kwargs)

class ReceiptProductViewSet(viewsets.ModelViewSet):
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
                    product = rp.product
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
                if inventory.goods_issued ==0 and inventory.goods_received ==0:
                    inventory.delete()
                else:
                    inventory.save()
            if rp.receipt.to_department:
                latest_inventory = Inventory.objects.filter(
                    department=rp.receipt.to_department,
                    product = rp.product
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
                if inventory.goods_issued ==0 and inventory.goods_received ==0:
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


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all().order_by('-year', '-month')
    serializer_class = InventorySerializer
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'year', 'month', 'product']


###


# class InventorySummaryViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = InventorySummarySerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filterset_fields = ['department', 'product']

#     def get_queryset(self):
#         grouped_records = Inventory.objects.values('department', 'product').annotate(
#             latest_id=Subquery(
#                 Inventory.objects.filter(
#                     department=OuterRef('department'),
#                     product=OuterRef('product')
#                 ).order_by('-year', '-month').values('id')[:1]
#             )
#         )

#         latest_records = Inventory.objects.filter(id__in=Subquery(grouped_records.values('latest_id'))).order_by('department', 'product')
#         return latest_records


class InventorySummaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventorySummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'product']

    def get_queryset(self):
        date_str = self.request.query_params.get('date', None)  # type: ignore
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            year, month = date.year, date.month
            # while True:
            # Try to retrieve inventory records for the specified year and month or earlier month
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
                # If there are inventory records for the specified month, retrieve the latest records
                latest_records = Inventory.objects.filter(id__in=Subquery(
                    grouped_records.values('latest_id'))).order_by('department', 'product')
                # break
            else:
                # If there are no inventory records for the specified month, retrieve for previous years
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
                    # break
                else:
                    # if no records for previous years
                    latest_records = Inventory.objects.none()
                    # break
            return latest_records
        else:
            # Retrieve the latest inventory records for each department and product
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
