from django.contrib import admin, messages
from api.models import Company, Employee


admin.site.register({Company, Employee})
