from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models.signals import pre_delete
from django.db.models import Count, Q
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Company, Employee
from .serializer import CompanySerializer, EmployeeSerializer
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100



@receiver(pre_delete, sender = Company)
def prevent_company_deletion(sender, instance, **kwargs):
    if instance.employees.exists():
        raise ValidationError(message = "This company cannot be deleted because it has employees.")


def extended_employees(request, serializer_class, data, fields=None, many=True):

    with_employees = request.GET.get('with_employees', '0') == '1'
    default_fields = ['id', 'name', 'address', 'phone', 'description', 'employee_count']

    if with_employees:
        fields = default_fields + ['employees']

    serializer = serializer_class(data, many=many, fields=fields)
    return Response(serializer.data, status=status.HTTP_200_OK)





@api_view(['GET', 'POST'])
def company_list(request):
    if request.method == 'GET':
        valid_ordering_fields = ['name', 'address', 'phone', 'description', 'employee_count']
        all_company = Company.objects.all()

        name = request.GET.get('name', None)
        address = request.GET.get('address', None)
        phone = request.GET.get('phone', None)
        description = request.GET.get('description', None)
        employees = request.GET.get('employees', None)

        if name:
            all_company = all_company.filter(name__icontains=name)
        if address:
            all_company = all_company.filter(address__icontains=address)
        if phone:
            all_company = all_company.filter(phone__icontains=phone)
        if description:
            all_company = all_company.filter(description__icontains=description)
        if employees:
            all_company = all_company.annotate(employee_count=Count('employees')).filter(employee_count=int(employees))



        search = request.GET.get('search', None)
        if search:
            all_company = all_company.filter(
                Q(id__icontains=search) |
                Q(name__icontains=search) |
                Q(address__icontains=search) |
                Q(phone__icontains=search) |
                Q(description__icontains=search)
            )
            if not all_company.exists():
                return Response(
                    {"message": f"No companies found matching the search criteria. ({search})"},
                    status=status.HTTP_404_NOT_FOUND
                )

        ordering = request.GET.get('ordering', None)
        if ordering:
            ordering_field = ordering.lstrip('-')
            if ordering_field not in valid_ordering_fields:
                return Response(
                    {"error": f"The submitted order query ({ordering_field}) is invalid! Use one of: {valid_ordering_fields}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if ordering_field == 'employee_count':
                all_company = all_company.annotate(employee_count=Count('employees'))
            all_company = all_company.order_by(ordering)
        else:
            all_company = all_company.order_by('name')

        all_company = all_company.distinct()


        paginator = CustomPagination()
        paginated_companies = paginator.paginate_queryset(all_company, request)


        if request.GET.get('with_employees') == '1':
            company_ids = [company.id for company in paginated_companies]
            employees_by_company = (
                Employee.objects.filter(company_id__in=company_ids)
                .values('company_id', 'id', 'name', 'job_title')
            )

            employees_map = {}
            for employee in employees_by_company:
                employees_map.setdefault(employee['company_id'], []).append(employee)

            serialized_companies = []
            for company in paginated_companies:
                company_data = CompanySerializer(
                    company, fields=['id', 'name', 'address', 'phone', 'description', 'employee_count']
                ).data
                company_data['employees'] = employees_map.get(company.id, [])
                serialized_companies.append(company_data)
        else:

            serialized_companies = CompanySerializer(
                paginated_companies, many=True, fields=['id', 'name', 'address', 'phone', 'description', 'employee_count']
            ).data


        return paginator.get_paginated_response(serialized_companies)
    

    if request.method == 'POST':
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'PATCH', 'DELETE'])
def manage_company(request, pk):
    try:
        company = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return Response({'error': 'Company not found!'}, status=status.HTTP_404_NOT_FOUND)


    if request.method == 'GET':
        return extended_employees(
            request, CompanySerializer, company,
            fields=['id', 'name', 'address', 'phone', 'description', 'employee_count'],
            many = False
        )

    if request.method == 'PATCH':
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            company.delete()
            return Response({'message': 'Company deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'POST'])
def employee_list(request):
    if request.method == 'GET':
        valid_ordering_fields = ['name', 'email', 'job_title', 'age', 'company']
        all_employee = Employee.objects.all()

        name = request.GET.get('name', None)
        email = request.GET.get('email', None)
        job_title = request.GET.get('job_title', None)
        age = request.GET.get('age', None)
        company_name = request.GET.get('company_name', None)

        if name:
            all_employee = all_employee.filter(name__icontains=name)
        if email:
            all_employee = all_employee.filter(email__icontains=email)
        if job_title:
            all_employee = all_employee.filter(job_title__icontains=job_title)
        if age:
            all_employee = all_employee.filter(age=age)
        if company_name:
            all_employee = all_employee.filter(company__name__icontains=company_name)

        if not all_employee.exists():
            return Response(
                    {"message": "No employees found matching the filtering criteria."},
                    status=status.HTTP_404_NOT_FOUND
                )

        search = request.GET.get('search', None)
        if search:
            all_employee = all_employee.filter(
                Q(id__icontains=search) |
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(job_title__icontains=search) |
                Q(age__icontains=search) |
                Q(company__name__icontains=search)
            )
            if not all_employee.exists():
                return Response(
                    {"message": f"No employees found matching the search criteria. ({search})"},
                    status=status.HTTP_404_NOT_FOUND
                )

        ordering = request.GET.get('ordering', None)
        if ordering:
            ordering_field = ordering.lstrip('-')
            if ordering_field not in valid_ordering_fields:
                return Response(
                    {"error": f"The submitted order query ({ordering_field}) is invalid! Use one of: {valid_ordering_fields}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            all_employee = all_employee.order_by(ordering)
        else:
            all_employee = all_employee.order_by('id')

        paginator = CustomPagination()
        paginated_data = paginator.paginate_queryset(all_employee, request)
        serializer = EmployeeSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)

    if request.method == 'POST':
        serializer = EmployeeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def manage_employee(request, pk):
    try:
        employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found!'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)

    if request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = EmployeeSerializer(employee, data=request.data, partial=partial, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        employee.delete()
        return Response({'message': 'Employee deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['POST', 'PUT', 'PATCH'])
def bulk_manage_employees(request):
    if request.method == 'POST':
        employees_data = request.data.get('employees', [])
        action = request.data.get('action', '').upper()

        if not isinstance(employees_data, list):
            return Response({'error': 'Employees data must be a list.'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'CREATE':
            serializer = EmployeeSerializer(data=employees_data, many=True, context={'request': request})
            
            if serializer.is_valid():
                try:

                    employees = [Employee(**data) for data in serializer.validated_data]
                    Employee.objects.bulk_create(employees)

                    
                    return Response({'message': f'{len(employees)} employees added.'}, status=status.HTTP_201_CREATED)

                except Exception as e:
                    return Response({'error': f'Error occurred: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

        if action == 'DELETE':
            employee_ids = [data.get('id') for data in employees_data if 'id' in data]
            
            if not employee_ids:
                return Response({'error': 'At least one ID is required for deletion.'}, status=status.HTTP_400_BAD_REQUEST)
            

            existing_employees = Employee.objects.filter(id__in=employee_ids)
            existing_ids = set(str(emp.id) for emp in existing_employees)


            non_existing_ids = [emp_id for emp_id in employee_ids if str(emp_id) not in existing_ids]

            deleted_count, _ = existing_employees.delete()

            if deleted_count > 0:
                if non_existing_ids:
                    return Response({
                        'message': f'{deleted_count} employees deleted. However, the following employee IDs do not exist: {", ".join(non_existing_ids)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': f'{deleted_count} employees deleted.'}, status=status.HTTP_200_OK)

            elif deleted_count == 0 and non_existing_ids:
                return Response({'error': 'Could not delete any entries. The submitted IDs are invalid.'}, status=status.HTTP_400_BAD_REQUEST)
            
    elif request.method in ['PUT', 'PATCH']:   
        partial = request.method == 'PATCH'
        employees_data = request.data

        with transaction.atomic():
            employees_to_update = []
            update_fields = []
            errors = []


            for data in employees_data:
                employee_id = data.get('id')
                if not employee_id:
                    errors.append({'error': 'Each update must include an ID.'})
                    continue

                try:
                    employee = Employee.objects.get(pk=employee_id)
                except Employee.DoesNotExist:
                    errors.append({'error': f'Employee ID {employee_id} not found.'})
                    continue


                serializer = EmployeeSerializer(employee, data=data, partial=partial, context={'request': request})
                if serializer.is_valid():
                    updated_employee = serializer.save()


                    update_fields = [field for field in serializer.validated_data.keys()]
                    employees_to_update.append(updated_employee)
                else:
                    errors.append(serializer.errors)


            if errors:
                return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)


            if employees_to_update:
                Employee.objects.bulk_update(employees_to_update, update_fields)

            return Response({'message': f'{len(employees_to_update)} employees updated.'}, status=status.HTTP_200_OK)
        
    return Response({'error': 'Invalid action. Make sure either "CREATE" or "DELETE" is provided.'}, status=status.HTTP_400_BAD_REQUEST)