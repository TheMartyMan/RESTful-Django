from django.db import models
import uuid
from django.core.validators import EmailValidator, RegexValidator




class Company(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.CharField(max_length = 100, null = False, blank = False)
    
    address = models.CharField(max_length = 200, null = False, blank = False)
    
    phone_validator = RegexValidator(
        regex = r'^(?:\+36|06)\d{9}$',
        message = "The phone number must begin with the prefix '+36' or '06' and contain 9 digits."
    )
    phone = models.CharField(
        max_length = 12,
        null = False,
        blank = False,
        validators = [phone_validator]
    )
    
    description = models.CharField(max_length = 200, blank = True, null = True)


    def __str__(self):
        return self.name




class Employee(models.Model):
    JOB_TITLES = [
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('manager', 'Manager'),
        ('tester', 'Tester'),
    ]
    
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.CharField(max_length = 100, null = False, blank = False)

    email = models.EmailField(
        unique = True,
        validators = [EmailValidator],
        null = False,
        blank = False
    )

    job_title = models.CharField(max_length = 50, choices = JOB_TITLES, null = False, blank = False)
    age = models.PositiveIntegerField(null = False, blank = False)

    company = models.ForeignKey(
        'Company',
        related_name = "employees",
        on_delete = models.CASCADE,
        null = False,
        blank = False
    )

    def __str__(self):
        return f"{self.name} ({self.job_title})"