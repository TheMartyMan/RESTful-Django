# Generated by Django 5.1.4 on 2025-01-14 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_company_address_alter_company_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(error_messages={'required': 'A mező nem lehet üres!'}, max_length=100),
        ),
    ]
