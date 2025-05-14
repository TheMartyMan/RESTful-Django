from rest_framework import serializers
from .models import Company, Employee
from collections import OrderedDict
import uuid



class EmployeeSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if request and '/api/employee/bulk/' in request.path:
            self.fields['company'] = serializers.UUIDField(required=True, validators=[self.validate_company])

        elif request and request.path.startswith('/api/employee/'):
            self.fields['company'] = serializers.UUIDField(required=True)

        elif request and request.path.startswith('/api/company/'):
            self.fields['company'] = serializers.SerializerMethodField()
        
        if 'company' in self.fields:
            fields = OrderedDict(self.fields)
            fields.move_to_end('company')
            self.fields = fields

    def create(self, validated_data):
        company_id = validated_data.pop('company')
        company = Company.objects.get(id=company_id)
        employee = Employee.objects.create(company=company, **validated_data)
        return employee

    def update(self, instance, validated_data):
        company_id = validated_data.pop('company', None)
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                raise serializers.ValidationError({'company': 'The specified company does not exist.'})
            instance.company = company

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def validate_age(self, value):
        if value < 16:
            raise serializers.ValidationError("Individuals under the age of 16 are not permitted to engage in employment.")
        return value
    
    def validate_company(self, value):
        request = self.context.get('request')
        if request and request.method == 'POST' and '/api/employee/bulk/' in request.path:
            if isinstance(value, uuid.UUID):
                try:
                    company = Company.objects.get(id=value)
                    return company
                except Company.DoesNotExist:
                    raise serializers.ValidationError(f"Company with UUID {value} does not exist.")
            else:
                raise serializers.ValidationError("Invalid company UUID.")
        else:
            return value

        
    def get_company(self, obj):
        if obj.company:
            return CompanySerializer(obj.company, fields=['id', 'name']).data
        return None




class CompanySerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()
    employees = EmployeeSerializer(many = True, required = False)

    class Meta:
        model = Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = list(fields)
            self.fields = OrderedDict((field, self.fields[field]) for field in allowed if field in self.fields)

    def get_employee_count(self, obj):
        return obj.employees.count()

    def create(self, validated_data):
        employees_data = validated_data.pop('employees', [])
        company = super().create(validated_data)
        
        for employee_data in employees_data:
            employee_data['company'] = company
            Employee.objects.create(**employee_data)

        return company