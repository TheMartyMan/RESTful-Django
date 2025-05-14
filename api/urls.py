from django.urls import path
from .views import company_list, manage_company, employee_list, manage_employee, bulk_manage_employees

urlpatterns = [
    path('company/', company_list, name='companies'),
    path('company/<uuid:pk>/', manage_company, name='company_detail'),
    path('employee/', employee_list, name='employees'),
    path('employee/<uuid:pk>/', manage_employee, name='employee_detail'),
    path('employee/bulk/', bulk_manage_employees, name='bulk_employee'),
]


