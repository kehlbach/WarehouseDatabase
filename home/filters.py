from django.urls import resolve
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import BaseFilterBackend

from home.models import Profile, Receipt, ReceiptProduct, RolePermission

from . import views


class ReceiptsFilterBackend(BaseFilterBackend):
    """with allowed_to only receipts from allowed departments are returned

    allowed_to expects Profile primary key"""

    def filter_queryset(self, request, queryset, view):
        # Get the value of the department query parameter
        department = request.query_params.get("department")
        allowed_to = request.query_params.get("allowed_to")
        if department:
            # Filter the queryset based on the department attribute
            queryset = queryset.filter(from_department=department) | queryset.filter(
                to_department=department
            )
        if allowed_to:
            try:
                # Get the profile instance with the specified profile_id
                profile = Profile.objects.get(id=allowed_to)

                # Filter the queryset based on the departments in the profile's departments attribute
                queryset = queryset.filter(
                    from_department__in=profile.departments.all()
                ) | queryset.filter(to_department__in=profile.departments.all())
            except Profile.DoesNotExist:
                # Return an empty queryset if no such profile is found
                queryset = queryset.none()
        return queryset


class DepartmentsFilterBackend(BaseFilterBackend):
    """with allowed_to only allowed departments are returned

    allowed_to expects Profile primary key"""

    def filter_queryset(self, request, queryset, view):
        # Get the profile_id query parameter from the request
        allowed_to = request.query_params.get("allowed_to")
        if allowed_to:
            try:
                # Get the profile instance with the specified profile_id
                profile = Profile.objects.get(id=allowed_to)

                # Get all departments allowed to the profile
                departments = profile.departments.all()

                # Filter the queryset to include only instances with a from_department or to_department in the allowed departments
                queryset = queryset.filter(id__in=departments)
            except Profile.DoesNotExist:
                # Return an empty queryset if no such profile is found
                queryset = queryset.none()
        return queryset.distinct()


class RequesterFilterBackend(BaseFilterBackend):
    """Check if the user has the right to perform the action
    fields: requester, intended_actions.

    -requester expects Telegram user_id

    -intended_actions options - VIEW, ADD, EDIT, DELETE
    Examples:
    >>> ..&intended_actions=VIEW..
    >>> ..&intended_actions=VIEW ADD..

    If several specified, returns if any of them is present

    if allowed_actions not present it is figured out by request type (GET POST etc.)
    """

    def filter_queryset(self, request, queryset, view):
        requester = request.query_params.get("requester")
        intended_actions = request.query_params.get("intended_actions")
        if requester:
            profile = Profile.objects.filter(user_id=requester).first()
            role_permissions = RolePermission.objects.filter(role=profile.role)  # type: ignore
            error = "You do not have permission to perform this action"
            if intended_actions:
                intended_actions = intended_actions.split(" ")
            else:
                intended_actions = [request.method]
            actions = []
            for each in intended_actions:
                match each.upper():
                    case "GET" | "VIEW":
                        action = RolePermission.VIEW
                    case "POST" | "ADD":
                        action = RolePermission.ADD
                    case "PATCH" | "PUT" | "EDIT":
                        action = RolePermission.EDIT
                    case "DELETE":
                        action = RolePermission.DELETE
                    case "ANY":
                        action = "ANY"
                    case _:
                        continue
                actions.append(action)
            view_func, args, kwargs = resolve(request.path_info)
            if isinstance(view, views.DepartmentViewSet):
                subject = RolePermission.DEPARTMENTS
            elif isinstance(view, (views.RoleViewSet, views.RolePermissionViewSet)):
                subject = RolePermission.ROLES
            elif isinstance(view, views.ProfileViewSet):
                subject = RolePermission.PROFILES
            elif isinstance(
                view, (views.InventoryViewSet, views.InventorySummaryViewSet)
            ):
                subject = RolePermission.INVENTORY
                if "department" in request.query_params:
                    if not profile.departments.filter(pk=request.query_params["department"]).exists():  # type: ignore
                        raise PermissionDenied(error)
            elif isinstance(view, (views.ReceiptViewSet, views.ReceiptProductViewSet)):
                subject = RolePermission.RECEIPTS
                if "pk" in kwargs:
                    if isinstance(view, views.ReceiptViewSet):
                        receipt = Receipt.objects.get(id=kwargs["pk"])
                    else:  # ReceiptProductViewSet
                        receipt_product = ReceiptProduct.objects.get(id=kwargs["pk"])
                        receipt = receipt_product.receipt
                    if (
                        receipt.from_department
                        and not receipt.from_department in profile.departments.all()
                    ) or (  # type: ignore
                        receipt.to_department
                        and not receipt.to_department in profile.departments.all()
                    ):  # type: ignore
                        raise PermissionDenied(error)
            elif isinstance(view, views.CategoryViewSet):
                subject = RolePermission.CATEGORIES
            elif isinstance(view, views.ProductViewSet):
                subject = RolePermission.PRODUCTS
            else:
                return queryset
            if "ANY" in actions:
                permission = []
                for each in [each[0] for each in RolePermission.Actions]:
                    temp = role_permissions.filter(action=each, subject=subject).first()
                    if temp:
                        permission.append(temp)
            else:
                permission = role_permissions.filter(
                    action__in=actions, subject=subject
                ).first()
            if not permission:
                raise PermissionDenied(error)
                # return Response({'error': error['detail']}, status=status.HTTP_403_FORBIDDEN)
        return queryset
