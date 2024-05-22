import django_filters
from .models import Employee

class EmployeeFilter(django_filters.FilterSet):
    company_name = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    project_name = django_filters.CharFilter(field_name='project__name', lookup_expr='icontains')

    class Meta:
        model = Employee
        fields = {
            'fullname': ['exact', 'icontains'],
            'mobile_number': ['exact', 'icontains'],
            'on_duty': ['exact'],
                    
            }
