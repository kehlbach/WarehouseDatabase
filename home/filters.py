from rest_framework.filters import BaseFilterBackend

from .models import *

class ReceiptsFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        # Get the value of the department query parameter
        department = request.query_params.get('department')
        allowed_to = request.query_params.get('allowed_to')
        if department:
            # Filter the queryset based on the department attribute
            queryset = queryset.filter(
                from_department=department) | queryset.filter(
                to_department=department)
        if allowed_to:
            try:
                # Get the profile instance with the specified profile_id
                profile = Profile.objects.get(id=allowed_to)

                # Filter the queryset based on the departments in the profile's departments attribute
                queryset = queryset.filter(
                    from_department__in=profile.departments.all()) | queryset.filter(
                    to_department__in=profile.departments.all())
            except Profile.DoesNotExist:
                # Return an empty queryset if no such profile is found
                queryset = queryset.none()
        return queryset
    
class DepartmentsFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        # Get the profile_id query parameter from the request
        allowed_to = request.query_params.get('allowed_to')
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