from django.urls import include, path
from rest_framework import routers
from home import views


router = routers.DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'permissions', views.PermissionViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'receipts', views.ReceiptViewSet)
router.register(r'receipt_products', views.ReceiptProductViewSet)
router.register(r'inventory', views.InventoryViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('actions/', views.ActionsView.as_view()),
    path('subjects/', views.SubjectsView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
